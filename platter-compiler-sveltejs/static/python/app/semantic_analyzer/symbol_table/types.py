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
    
    def __init__(self, base_type: str, dimensions: int = 0, table_fields: Optional[Dict[str, 'TypeInfo']] = None, array_sizes: Optional[List[int]] = None):
        self.base_type = base_type
        self.dimensions = dimensions if dimensions is not None else 0
        self.table_fields = table_fields or {}
        self.is_table = table_fields is not None
        self.array_sizes = array_sizes or []  # List of sizes for each dimension (outermost first)
    
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
        self.value = None  # Store the computed default value for display
    
    def add_usage(self, scope_name: str, declared_scope_name: str):
        """Record that this symbol was accessed in a given scope (only if different from declaration scope)"""
        # Only record if accessed in a different scope than where it was declared
        if scope_name != declared_scope_name and scope_name not in self.accessed_in_scopes:
            self.accessed_in_scopes.append(scope_name)
    
    def compute_default_value(self, table_types: Dict[str, TypeInfo] = None):
        """Compute and set the default value based on type and kind"""
        table_types = table_types or {}
        
        # For recipes, return default value of return type
        if self.kind == SymbolKind.FUNCTION:
            self.value = self._get_type_default(self.type_info, table_types)
            return self.value
        
        # For table prototypes, return field structure
        if self.kind == SymbolKind.TABLE_TYPE:
            fields = []
            for field_name, field_type in self.type_info.table_fields.items():
                dims_str = '[]' * field_type.dimensions if field_type.dimensions > 0 else ''
                fields.append(f"{field_name}: {field_type.base_type}{dims_str}")
            self.value = "{ " + ", ".join(fields) + " }"
            return self.value
        
        # For variables/parameters, check if initialized
        if self.declaration_node and hasattr(self.declaration_node, 'init_value'):
            init_value = self.declaration_node.init_value
            if init_value:
                self.value = self._extract_value_from_node(init_value, table_types)
                return self.value
        
        # Return type default for uninitialized variables
        self.value = self._get_type_default(self.type_info, table_types)
        return self.value
    
    def _get_type_default(self, type_info: TypeInfo, table_types: Dict[str, TypeInfo]) -> str:
        """Get default value string for a type"""
        # Arrays
        if type_info.dimensions > 0:
            return f"[{type_info.base_type}]" + '[]' * (type_info.dimensions - 1)
        
        # Table instances
        if type_info.is_table and type_info.table_fields:
            fields = []
            for field_name, field_type in type_info.table_fields.items():
                default_val = self._get_type_default(field_type, table_types)
                fields.append(f"{field_name}: {default_val}")
            return "{ " + ", ".join(fields) + " }"
        
        # Primitives
        if type_info.base_type == "piece":
            return "0"
        elif type_info.base_type == "sip":
            return "0.0"
        elif type_info.base_type == "chars":
            return '""'
        elif type_info.base_type == "flag":
            return "down"
        else:
            # Unknown or custom types
            return "-"
    
    def _extract_value_from_node(self, node, table_types: Dict[str, TypeInfo]) -> str:
        """Extract value from an AST node"""
        from app.semantic_analyzer.ast.ast_nodes import Literal, ArrayLiteral, TableLiteral, Identifier, BinaryOp
        
        if isinstance(node, Literal):
            val = node.value
            # Convert based on value_type since tokens store everything as strings
            if node.value_type == "piece":
                # Numeric integer
                return str(val)  # Already a string from token, just return as-is
            elif node.value_type == "sip":
                # Numeric float
                return str(val)  # Already a string from token
            elif node.value_type == "chars":
                # String literal - check if value already includes quotes
                # Lexer tokens have quotes: '"hello"'
                # Programmatically created literals don't: "hello"
                if val and val[0] == '"' and val[-1] == '"':
                    return str(val)  # Already has quotes
                else:
                    return f'"{val}"'  # Add quotes
            elif node.value_type == "flag":
                # Boolean - convert "up"/"down" or True/False to up/down
                if isinstance(val, bool):
                    return "up" if val else "down"
                elif isinstance(val, str):
                    # Token value is "up" or "down"
                    return val
                else:
                    return "up" if val else "down"
            else:
                # Unknown type
                return str(val)
        
        elif isinstance(node, ArrayLiteral):
            if not node.elements:
                # Empty array - show element type
                elem_type = self.type_info.get_element_type()
                if elem_type:
                    return f"[{elem_type.base_type}]"
                return "[]"
            else:
                # Show array with count
                elem_type = self.type_info.get_element_type()
                if elem_type:
                    return f"[{len(node.elements)} × {elem_type.base_type}]"
                return f"[{len(node.elements)}]"
        
        elif isinstance(node, TableLiteral):
            fields = []
            for field_name, value, line, col in node.field_inits:
                val_str = self._extract_value_from_node(value, table_types)
                fields.append(f"{field_name}: {val_str}")
            return "{ " + ", ".join(fields) + " }"
        
        elif isinstance(node, Identifier):
            return f"@{node.name}"
        
        elif isinstance(node, BinaryOp):
            # For expressions, show the result type
            return f"<{self.type_info.base_type}>"
        
        else:
            # Other expressions
            return f"<{self.type_info.base_type}>"
    
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
