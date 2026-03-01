"""
Semantic Analyzer Module for Platter Language

Main entry point for semantic analysis with modular passes:
- Symbol table building (collects symbols and scope information)
- Scope checking (undefined symbols, duplicate definitions)
- Type checking (type compatibility, operations)
- Control flow checking (stop/next, serve statements)
- Recipe checking (flavor count, flavor types)
"""

from .semantic_analyzer import (
    SemanticAnalyzer,
    analyze_program
)

from .symbol_table import (
    SymbolTable,
    SymbolTableBuilder,
    Symbol,
    SymbolKind,
    TypeInfo,
    Scope,
    build_symbol_table,
    print_symbol_table
)

from .semantic_passes import (
    SemanticError,
    SemanticErrorHandler,
    ErrorSeverity,
    ErrorCodes,
    TypeChecker,
    ScopeChecker,
    ControlFlowChecker,
    FunctionChecker
)

from .builtin_recipes import (
    BuiltinRecipeSignature,
    BUILTIN_RECIPES,
    get_builtin_recipe,
    is_builtin_recipe,
    get_all_builtin_recipe_names
)

__all__ = [
    # Main analyzer
    'SemanticAnalyzer',
    'analyze_program',
    
    # Symbol table
    'SymbolTable',
    'SymbolTableBuilder',
    'Symbol',
    'SymbolKind',
    'TypeInfo',
    'Scope',
    'build_symbol_table',
    'print_symbol_table',
    
    # Error handling
    'SemanticError',
    'SemanticErrorHandler',
    'ErrorSeverity',
    'ErrorCodes',
    
    # Semantic passes
    'TypeChecker',
    'ScopeChecker',
    'ControlFlowChecker',
    'FunctionChecker',
    
    # Built-in recipes
    'BuiltinRecipeSignature',
    'BUILTIN_RECIPES',
    'get_builtin_recipe',
    'is_builtin_recipe',
    'get_all_builtin_recipe_names'
]
