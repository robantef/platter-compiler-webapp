"""
Core Type System and Symbol Definitions for Platter Language
Contains the fundamental data structures used throughout semantic analysis
"""

from app.semantic_analyzer.ast.ast_nodes import ASTNode
from typing import Optional, Dict, List
from enum import Enum


class SymbolKind(Enum):
    """Types of symbols in the symbol table"""
    VARIABLE = "ingredient"  # variable -> ingredient
    PARAMETER = "spice"  # parameter -> spice
    FUNCTION = "recipe"  # function -> recipe
    TABLE_TYPE = "table_type"  # struct -> table
    FIELD = "field"


class TypeInfo:
    """Represents type information including arrays and nested structures"""
    
    def __init__(self, base_type: str, dimensions: int = 0, table_fields: Optional[Dict[str, 'TypeInfo']] = None):
        self.base_type = base_type
        self.dimensions = dimensions if dimensions is not None else 0
        self.table_fields = table_fields or {}
        self.is_table = table_fields is not None
    
    def __repr__(self):
        dims = f"{'[]' * self.dimensions}" if self.dimensions > 0 else ""
        if self.is_table:
            return f"Table({self.base_type}){dims}"
        return f"{self.base_type}{dims}"
    
    def __eq__(self, other):
        if not isinstance(other, TypeInfo):
            return False
        return (self.base_type == other.base_type and 
                self.dimensions == other.dimensions and
                self.is_table == other.is_table)
    
    def is_exact_match(self, other: 'TypeInfo') -> bool:
        """Check if this type exactly matches another (no implicit conversions)"""
        if self == other:
            return True
        if self.dimensions != other.dimensions:
            return False
        # Allow unknown base type to match any base type (for empty array inference)
        if self.base_type == "unknown" or other.base_type == "unknown":
            return True
        # No implicit promotion between piece and sip for assignments
        if self.base_type != other.base_type:
            return False
        if self.is_table and other.is_table:
            if set(self.table_fields.keys()) != set(other.table_fields.keys()):
                return False
            for field_name in self.table_fields:
                if not self.table_fields[field_name].is_exact_match(other.table_fields[field_name]):
                    return False
        return True
    
    def is_compatible_with(self, other: 'TypeInfo') -> bool:
        """Check if this type is compatible with another"""
        if self == other:
            return True
        if self.dimensions != other.dimensions:
            return False
        # Allow unknown base type to match any base type (for empty array inference)
        if self.base_type == "unknown" or other.base_type == "unknown":
            return True
        if self.base_type != other.base_type:
            # piece and sip are compatible
            if {self.base_type, other.base_type} == {"piece", "sip"}:
                return True
            return False
        if self.is_table and other.is_table:
            if set(self.table_fields.keys()) != set(other.table_fields.keys()):
                return False
            for field_name in self.table_fields:
                if not self.table_fields[field_name].is_compatible_with(other.table_fields[field_name]):
                    return False
        return True
    
    def get_element_type(self) -> Optional['TypeInfo']:
        """Get the type of array elements"""
        if self.dimensions == 0:
            return None
        return TypeInfo(self.base_type, self.dimensions - 1, self.table_fields if self.is_table else None)
    
    def get_field_type(self, field_name: str) -> Optional['TypeInfo']:
        """Get the type of a table field"""
        if not self.is_table:
            return None
        return self.table_fields.get(field_name)


class Symbol:
    """Represents a symbol in the symbol table"""
    
    def __init__(self, name: str, kind: SymbolKind, type_info: TypeInfo, 
                 scope_level: int, declaration_node: ASTNode = None, declared_scope: 'Scope' = None):
        self.name = name
        self.kind = kind
        self.type_info = type_info
        self.scope_level = scope_level
        self.declaration_node = declaration_node
        self.declared_scope = declared_scope  # Store the scope where declared
        self.is_initialized = False
        self.usages = []  # List of scope names where this symbol is accessed
        self.accessed_in_scopes = []  # Track unique scope names where accessed
    
    def add_usage(self, scope_name: str, declared_scope_name: str):
        """Record that this symbol was accessed in a given scope (only if different from declaration scope)"""
        # Only record if accessed in a different scope than where it was declared
        if scope_name != declared_scope_name and scope_name not in self.accessed_in_scopes:
            self.accessed_in_scopes.append(scope_name)
    
    def __repr__(self):
        return f"Symbol({self.name}: {self.type_info}, kind={self.kind.value}, level={self.scope_level})"


class Scope:
    """Represents a lexical scope"""
    
    def __init__(self, name: str, level: int, parent: Optional['Scope'] = None):
        self.name = name
        self.level = level
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.children: List['Scope'] = []
        self.declaring_scope = None  # The scope where this scope's symbols are declared
    
    def define(self, symbol: Symbol) -> bool:
        """Define a symbol in this scope"""
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True
    
    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Look up symbol in this scope only"""
        return self.symbols.get(name)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up symbol in this scope and parent scopes"""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
    
    def get_all_symbols(self) -> Dict[str, Symbol]:
        """Get all symbols visible in this scope"""
        all_symbols = {}
        if self.parent:
            all_symbols = self.parent.get_all_symbols()
        all_symbols.update(self.symbols)
        return all_symbols
    
    def __repr__(self):
        return f"Scope({self.name}, level={self.level}, symbols={len(self.symbols)})"
