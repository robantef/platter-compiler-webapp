"""
Symbol Table Output Utilities
Provides helper functions for formatting and displaying symbol table information
"""

from app.semantic_analyzer.symbol_table import SymbolTable, Symbol, Scope, SymbolKind
from app.semantic_analyzer.ast.ast_nodes import Literal, ArrayLiteral, TableLiteral, Identifier
from typing import List, Optional, Tuple


def _get_parameters_str(symbol: Symbol) -> str:
    """Get parameter list for functions"""
    if symbol.kind.value != 'recipe' or not symbol.declaration_node:
        return "-"
    
    if hasattr(symbol.declaration_node, 'params'):
        params = symbol.declaration_node.params
        if not params:
            return "()"
        param_strs = []
        for p in params:
            dims_str = f"[{p.dimensions}]" if hasattr(p, 'dimensions') and p.dimensions else ""
            param_id = p.identifier if hasattr(p, 'identifier') else ""
            param_strs.append(f"{p.data_type}{dims_str} {param_id}".strip())
        return f"({', '.join(param_strs)})"
    return "-"


def format_symbol_table_compact(symbol_table: SymbolTable, error_handler=None) -> str:
    """
    Format symbol table in a nicely formatted table with columns
    Separates built-in recipes from user-defined symbols
    
    Args:
        symbol_table: The symbol table to format
        error_handler: Optional error handler for displaying errors
    
    Returns:
        Formatted string representation
    """
    output = []
    
    # === BUILT-IN RECIPES SECTION ===
    if hasattr(symbol_table, 'builtin_recipes') and symbol_table.builtin_recipes:
        output.append("╔════════════════════════════════════════════════════════════════════════╗")
        output.append("║                      BUILT-IN RECIPES (OVERLOADABLE)                   ║")
        output.append("╚════════════════════════════════════════════════════════════════════════╝")
        output.append("")
        
        builtin_data = []
        for recipe_name, overloads in sorted(symbol_table.builtin_recipes.items()):
            for idx, symbol in enumerate(overloads, 1):
                params_str = _get_parameters_str(symbol)
                return_type = symbol.type_info.base_type
                return_dims = "[]" * symbol.type_info.dimensions if symbol.type_info.dimensions > 0 else ""
                
                builtin_data.append({
                    'name': recipe_name if idx == 1 else "",  # Show name only once
                    'overload': f"#{idx}",
                    'parameters': params_str,
                    'returns': f"{return_type}{return_dims}"
                })
        
        if builtin_data:
            # Calculate column widths
            max_name = max(len(b['name']) for b in builtin_data)
            max_overload = max(len(b['overload']) for b in builtin_data)
            max_params = max(len(b['parameters']) for b in builtin_data)
            max_returns = max(len(b['returns']) for b in builtin_data)
            
            name_width = max(max_name, len("Recipe")) + 2
            overload_width = max(max_overload, len("Ver")) + 2
            params_width = min(max(max_params, len("Parameters")) + 2, 50)
            returns_width = max(max_returns, len("Returns")) + 2
            
            # Build table header
            output.append("┌" + "─" * name_width + "┬" + "─" * overload_width + "┬" + 
                         "─" * params_width + "┬" + "─" * returns_width + "┐")
            
            header = (f"│ {'Recipe':<{name_width-2}} │ {'Ver':<{overload_width-2}} │ "
                     f"{'Parameters':<{params_width-2}} │ {'Returns':<{returns_width-2}} │")
            output.append(header)
            
            output.append("├" + "─" * name_width + "┼" + "─" * overload_width + "┼" + 
                         "─" * params_width + "┼" + "─" * returns_width + "┤")
            
            # Add data rows
            current_recipe = None
            for data in builtin_data:
                # Add separator between different recipes
                if current_recipe != data['name'] and data['name'] and current_recipe is not None:
                    output.append("├" + "─" * name_width + "┼" + "─" * overload_width + "┼" + 
                                 "─" * params_width + "┼" + "─" * returns_width + "┤")
                
                if data['name']:
                    current_recipe = data['name']
                
                params_display = data['parameters'][:params_width-2] if len(data['parameters']) > params_width-2 else data['parameters']
                
                row = (f"│ {data['name']:<{name_width-2}} │ {data['overload']:<{overload_width-2}} │ "
                      f"{params_display:<{params_width-2}} │ {data['returns']:<{returns_width-2}} │")
                output.append(row)
            
            # Close table
            output.append("└" + "─" * name_width + "┴" + "─" * overload_width + "┴" + 
                         "─" * params_width + "┴" + "─" * returns_width + "┘")
        
        output.append("")
        output.append("╔════════════════════════════════════════════════════════════════════════╗")
        output.append("║                      USER-DEFINED SYMBOLS                              ║")
        output.append("╚════════════════════════════════════════════════════════════════════════╝")
        output.append("")
    
    # === USER-DEFINED SYMBOLS SECTION ===
    # Collect all symbols with their scope information
    symbols_data = []
    
    def get_scope_type(scope_name: str, level: int) -> str:
        """Determine scope type from name and level - return descriptive scope name"""
        if level == 0:
            return "global"
        # Return the actual scope name which contains recipe names and statement types
        return scope_name
    
    def get_value_str(symbol: Symbol) -> str:
        """Get the computed default value from the symbol"""
        return symbol.value if symbol.value is not None else "-"
    
    def get_position_str(symbol: Symbol) -> str:
        """Get declaration position if available"""
        # Position info not currently in AST nodes, return placeholder
        return "N/A"
    
    def collect_symbols(scope: Scope) -> None:
        for name, symbol in scope.symbols.items():
            # Get the actual scope name where declared
            declared_scope_name = symbol.declared_scope.name if symbol.declared_scope else ""
            
            # Format accessed scopes as a list
            accessed_list = symbol.accessed_in_scopes if symbol.accessed_in_scopes else []
            accessed_str = ", ".join(accessed_list) if accessed_list else "-"
            
            # Format type display
            type_display = symbol.type_info.base_type
            if symbol.kind == SymbolKind.TABLE_TYPE:
                # Show as table prototype
                type_display = f"table<{symbol.type_info.base_type}>"
            elif symbol.type_info.is_table:
                # Show table instance with arrow
                type_display = f"→{symbol.type_info.base_type}"
            
            symbols_data.append({
                'id': symbol.name,
                'type': type_display,
                'dims': str(symbol.type_info.dimensions) if symbol.type_info.dimensions > 0 else "-",
                'declared_scope': declared_scope_name if declared_scope_name else "-",
                'accessed_scopes': accessed_str,
                'accessed_list': accessed_list,  # Store as list for console output
                'parameters': _get_parameters_str(symbol),
                'args': "-",  # Args tracked at call sites, not in symbol definition
                'value': get_value_str(symbol),
                'kind': symbol.kind.value,
                'scope_name': scope.name if declared_scope_name else "undeclared",
                'level': scope.level
            })
        
        for child in scope.children:
            collect_symbols(child)
    
    collect_symbols(symbol_table.global_scope)
    
    # Add undeclared symbols
    if hasattr(symbol_table, 'undeclared_symbols'):
        for name, symbol in symbol_table.undeclared_symbols.items():
            accessed_list = symbol.accessed_in_scopes if symbol.accessed_in_scopes else []
            accessed_str = ", ".join(accessed_list) if accessed_list else "-"
            
            symbols_data.append({
                'id': symbol.name,
                'type': symbol.type_info.base_type if symbol.type_info.base_type != "unknown" else "?",
                'dims': str(symbol.type_info.dimensions) if symbol.type_info.dimensions > 0 else "-",
                'declared_scope': "-",  # Empty for undeclared
                'accessed_scopes': accessed_str,
                'accessed_list': accessed_list,
                'parameters': "-",
                'args': "-",
                'value': "-",
                'kind': symbol.kind.value,
                'scope_name': "undeclared",
                'level': -1
            })
    
    # Calculate column widths
    if symbols_data:
        max_id = max(len(s['id']) for s in symbols_data)
        max_type = max(len(s['type']) for s in symbols_data)
        max_dims = max(len(s['dims']) for s in symbols_data)
        max_declared = max(len(s['declared_scope']) for s in symbols_data)
        max_accessed = max(len(s['accessed_scopes']) for s in symbols_data)
        max_params = max(len(s['parameters']) for s in symbols_data)
        max_args = max(len(s['args']) for s in symbols_data)
        max_value = max(len(s['value']) for s in symbols_data)
        
        # Set minimum widths
        id_width = max(max_id, len("ID")) + 2
        type_width = max(max_type, len("Type")) + 2
        dims_width = max(max_dims, len("Dims")) + 2
        declared_width = min(max(max_declared, len("Declared")) + 2, 25)  # Cap at 25
        accessed_width = min(max(max_accessed, len("Accessed")) + 2, 25)  # Cap at 25
        params_width = min(max(max_params, len("Parameters")) + 2, 35)  # Cap at 35
        args_width = max(max_args, len("Args")) + 2
        value_width = min(max(max_value, len("Value")) + 2, 50)  # Cap at 50 for more detail
        
        # Build table header with Unicode box-drawing characters
        output.append("┌" + "─" * id_width + "┬" + "─" * type_width + "┬" + "─" * dims_width + "┬" + 
                     "─" * declared_width + "┬" + "─" * accessed_width + "┬" + "─" * params_width + "┬" + 
                     "─" * args_width + "┬" + "─" * value_width + "┐")
        
        header = (f"│ {'ID':<{id_width-2}} │ {'Type':<{type_width-2}} │ {'Dims':<{dims_width-2}} │ "
                 f"{'Declared':<{declared_width-2}} │ {'Accessed':<{accessed_width-2}} │ {'Parameters':<{params_width-2}} │ "
                 f"{'Args':<{args_width-2}} │ {'Value':<{value_width-2}} │")
        output.append(header)
        
        output.append("├" + "─" * id_width + "┼" + "─" * type_width + "┼" + "─" * dims_width + "┼" + 
                     "─" * declared_width + "┼" + "─" * accessed_width + "┼" + "─" * params_width + "┼" + 
                     "─" * args_width + "┼" + "─" * value_width + "┤")
        
        # Group by scope level and scope for better readability
        # Put undeclared symbols at the end
        symbols_data.sort(key=lambda x: (999 if x['level'] == -1 else x['level'], x['scope_name'], x['kind'], x['id']))
        
        # Add data rows
        current_scope = None
        for data in symbols_data:
            # Add separator between different scopes
            if current_scope != data['scope_name']:
                if current_scope is not None:
                    output.append("├" + "─" * id_width + "┼" + "─" * type_width + "┼" + "─" * dims_width + "┼" + 
                                 "─" * declared_width + "┼" + "─" * accessed_width + "┼" + "─" * params_width + "┼" + 
                                 "─" * args_width + "┼" + "─" * value_width + "┤")
                current_scope = data['scope_name']
            
            # Truncate long values
            declared_display = data['declared_scope'][:declared_width-2] if len(data['declared_scope']) > declared_width-2 else data['declared_scope']
            accessed_display = data['accessed_scopes'][:accessed_width-2] if len(data['accessed_scopes']) > accessed_width-2 else data['accessed_scopes']
            params_display = data['parameters'][:params_width-2] if len(data['parameters']) > params_width-2 else data['parameters']
            value_display = data['value'][:value_width-2] if len(data['value']) > value_width-2 else data['value']
            
            row = (f"│ {data['id']:<{id_width-2}} │ {data['type']:<{type_width-2}} │ {data['dims']:<{dims_width-2}} │ "
                  f"{declared_display:<{declared_width-2}} │ {accessed_display:<{accessed_width-2}} │ {params_display:<{params_width-2}} │ "
                  f"{data['args']:<{args_width-2}} │ {value_display:<{value_width-2}} │")
            output.append(row)
        
        # Close table
        output.append("└" + "─" * id_width + "┴" + "─" * type_width + "┴" + "─" * dims_width + "┴" + 
                     "─" * declared_width + "┴" + "─" * accessed_width + "┴" + "─" * params_width + "┴" + 
                     "─" * args_width + "┴" + "─" * value_width + "┘")
    else:
        output.append("┌─────────────────────────────────┐")
        output.append("│  No symbols in symbol table     │")
        output.append("└─────────────────────────────────┘")
    
    # Add statistics with Unicode box-drawing characters
    output.append("")
    output.append("╔════════════════════════════════════════════╗")
    output.append("║      SYMBOL TABLE STATISTICS               ║")
    output.append("╠════════════════════════════════════════════╣")
    
    summary = format_symbol_table_summary(symbol_table, error_handler)
    output.append(f"║  Total Symbols:    {summary['total_symbols']:>4}                      ║")
    output.append(f"║  Variables:        {summary['variables']:>4}                      ║")
    output.append(f"║  Functions:        {summary['functions']:>4}                      ║")
    output.append(f"║  Table Types:      {summary['table_types']:>4}                      ║")
    output.append(f"║  Parameters:       {summary['parameters']:>4}                      ║")
    output.append("╠════════════════════════════════════════════╣")
    output.append(f"║  Errors:           {summary['errors']:>4}                      ║")
    output.append(f"║  Warnings:         {summary['warnings']:>4}                      ║")
    output.append("╚════════════════════════════════════════════╝")
    
    # Add error details if any
    if error_handler and error_handler.has_errors():
        errors = error_handler.get_errors()
        output.append("")
        output.append("╔════════════════════════════════════════════════════════════════════════╗")
        output.append("║                         SEMANTIC ISSUES                                ║")
        output.append("╠════════════════════════════════════════════════════════════════════════╣")
        
        for i, error in enumerate(errors, 1):
            severity_icon = "❌" if error.severity == "error" else "⚠️"
            output.append(f"║ {severity_icon} [{error.severity.name.upper():<7}] {error.message:<55} ║")
        
        output.append("╚════════════════════════════════════════════════════════════════════════╝")
    else:
        output.append("")
        output.append("✅ No semantic errors or warnings found!")
    
    return "\n".join(output)


def format_symbol_table_for_console(symbol_table: SymbolTable) -> List[dict]:
    """
    Format symbol table as a list of dictionaries for JavaScript console.table() output
    This format allows accessed scopes to be displayed as arrays without clipping
    
    Args:
        symbol_table: The symbol table to format
    
    Returns:
        List of dictionaries for each symbol
    """
    symbols_output = []
    
    def get_value_str(symbol: Symbol) -> str:
        """Get initial value if available"""
        if not symbol.declaration_node:
            return "-"
        
        node = symbol.declaration_node
        if hasattr(node, 'init_value') and node.init_value:
            if isinstance(node.init_value, Literal):
                return str(node.init_value.value)
            elif isinstance(node.init_value, ArrayLiteral):
                return f"[{len(node.init_value.elements)} items]"
            elif isinstance(node.init_value, TableLiteral):
                return f"{{{len(node.init_value.field_inits)} fields}}"
            else:
                return "<expr>"
        return "-"
    
    def collect_symbols(scope: Scope) -> None:
        for name, symbol in scope.symbols.items():
            # Get the actual scope name where declared
            declared_scope_name = symbol.declared_scope.name if symbol.declared_scope else ""
            
            # Format type display
            type_display = symbol.type_info.base_type
            if symbol.kind == SymbolKind.TABLE_TYPE:
                # Show as table prototype
                type_display = f"table<{symbol.type_info.base_type}>"
            elif symbol.type_info.is_table:
                # Show table instance with arrow
                type_display = f"→{symbol.type_info.base_type}"
            
            # Create dictionary with all symbol info
            symbol_dict = {
                'ID': symbol.name,
                'Type': type_display,
                'Dims': str(symbol.type_info.dimensions) if symbol.type_info.dimensions > 0 else "-",
                'Declared': declared_scope_name if declared_scope_name else "-",
                'Accessed': symbol.accessed_in_scopes if symbol.accessed_in_scopes else [],
                'Parameters': _get_parameters_str(symbol),
                'Value': get_value_str(symbol),
                'Kind': symbol.kind.value,
                'Level': scope.level
            }
            
            symbols_output.append(symbol_dict)
        
        for child in scope.children:
            collect_symbols(child)
    
    collect_symbols(symbol_table.global_scope)
    
    # Add undeclared symbols that were accessed
    if hasattr(symbol_table, 'undeclared_symbols'):
        for name, symbol in symbol_table.undeclared_symbols.items():
            symbol_dict = {
                'ID': symbol.name,
                'Type': symbol.type_info.base_type if symbol.type_info.base_type != "unknown" else "?",
                'Dims': str(symbol.type_info.dimensions) if symbol.type_info.dimensions > 0 else "-",
                'Declared': "",  # Empty for undeclared
                'Accessed': symbol.accessed_in_scopes if symbol.accessed_in_scopes else [],
                'Parameters': "-",
                'Value': "-",
                'Kind': symbol.kind.value,
                'Level': -1
            }
            symbols_output.append(symbol_dict)
    
    # Sort by level and name for better readability
    symbols_output.sort(key=lambda x: (x['Level'], x['ID']))
    
    return symbols_output


def format_symbol_table_summary(symbol_table: SymbolTable, error_handler=None) -> dict:
    """
    Create a summary dictionary of symbol table statistics
    
    Args:
        symbol_table: The symbol table to summarize
    
    Returns:
        Dictionary with statistics
    """
    def count_symbols_in_scope(scope: Scope) -> dict:
        counts = {
            'total': len(scope.symbols),
            'variables': 0,
            'functions': 0,
            'tables': 0,
            'parameters': 0
        }
        
        for symbol in scope.symbols.values():
            kind = symbol.kind.value
            if kind == 'variable':
                counts['variables'] += 1
            elif kind == 'function':
                counts['functions'] += 1
            elif kind == 'table_type':
                counts['tables'] += 1
            elif kind == 'parameter':
                counts['parameters'] += 1
        
        # Add children counts
        for child in scope.children:
            child_counts = count_symbols_in_scope(child)
            for key in counts:
                counts[key] += child_counts[key]
        
        return counts
    
    counts = count_symbols_in_scope(symbol_table.global_scope)
    
    error_count = 0
    warning_count = 0
    has_errors = False
    
    if error_handler:
        from app.semantic_analyzer.semantic_passes.error_handler import ErrorSeverity
        errors = error_handler.get_errors()
        error_count = len([e for e in errors if e.severity == ErrorSeverity.ERROR])
        warning_count = len([e for e in errors if e.severity == ErrorSeverity.WARNING])
        has_errors = error_handler.has_errors()
    
    return {
        'total_symbols': counts['total'],
        'variables': counts['variables'],
        'functions': counts['functions'],
        'table_types': counts['tables'],
        'parameters': counts['parameters'],
        'errors': error_count,
        'warnings': warning_count,
        'has_errors': has_errors
    }


def get_symbol_table_status_message(symbol_table: SymbolTable, error_handler=None) -> str:
    """
    Get a short status message about the symbol table analysis
    
    Args:
        symbol_table: The symbol table to check
        error_handler: Optional error handler
    
    Returns:
        Status message string
    """
    summary = format_symbol_table_summary(symbol_table, error_handler)
    
    if summary['has_errors']:
        return f"Symbol Table: {summary['errors']} error(s), {summary['warnings']} warning(s)"
    elif summary['warnings'] > 0:
        return f"Symbol Table: OK with {summary['warnings']} warning(s)"
    else:
        return f"Symbol Table: OK - {summary['total_symbols']} symbols defined"


def format_errors_only(error_handler) -> str:
    """
    Format only the errors from the error handler
    
    Args:
        error_handler: The error handler to get errors from
    
    Returns:
        Formatted error string
    """
    if not error_handler or not error_handler.has_errors():
        return "No errors or warnings"
    
    output = []
    for error in error_handler.get_errors():
        output.append(f"[{error.severity.name.upper()}] {error.message}")
    
    return "\n".join(output)


def get_all_symbols_flat(symbol_table: SymbolTable) -> List[Symbol]:
    """
    Get a flat list of all symbols from all scopes
    
    Args:
        symbol_table: The symbol table to extract from
    
    Returns:
        List of all Symbol objects (including undeclared but accessed symbols)
    """
    symbols = []
    
    def collect_from_scope(scope: Scope):
        symbols.extend(scope.symbols.values())
        for child in scope.children:
            collect_from_scope(child)
    
    collect_from_scope(symbol_table.global_scope)
    
    # Add undeclared but accessed symbols
    if hasattr(symbol_table, 'undeclared_symbols'):
        symbols.extend(symbol_table.undeclared_symbols.values())
    
    return symbols


def find_symbol_by_name(symbol_table: SymbolTable, name: str) -> Optional[Symbol]:
    """
    Find a symbol by name across all scopes
    
    Args:
        symbol_table: The symbol table to search
        name: Name of the symbol to find
    
    Returns:
        First matching Symbol or None
    """
    all_symbols = get_all_symbols_flat(symbol_table)
    for symbol in all_symbols:
        if symbol.name == name:
            return symbol
    return None


# Example usage
if __name__ == "__main__":
    from app.semantic_analyzer.ast.ast_nodes import *
    from app.semantic_analyzer.symbol_table import build_symbol_table
    
    # Create a simple test AST
    program = Program()
    
    # Add a variable
    var_decl = IngrDecl("piece", "testVar", Literal("piece", 42))
    program.add_global_decl(var_decl)
    
    # Add a function
    params = [ParamDecl("piece", 0, "x")]
    body = Platter()
    recipe = RecipeDecl("piece", 0, "double", params, body)
    program.add_recipe_decl(recipe)
    
    # Build symbol table
    symbol_table = build_symbol_table(program)
    
    # Test formatting functions
    print("=== Compact Format ===")
    print(format_symbol_table_compact(symbol_table))
    
    print("\n=== Summary ===")
    print(format_symbol_table_summary(symbol_table))
    
    print("\n=== Status Message ===")
    print(get_symbol_table_status_message(symbol_table))
