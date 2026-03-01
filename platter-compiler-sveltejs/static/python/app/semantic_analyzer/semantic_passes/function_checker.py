"""
Recipe Checking Pass for Platter Language
Validates recipe calls, spice (parameter) matching, and serve (return) types
"""

from app.semantic_analyzer.ast.ast_nodes import *
from app.semantic_analyzer.symbol_table.types import TypeInfo, Symbol, SymbolKind
from app.semantic_analyzer.symbol_table.symbol_table import SymbolTable
from app.semantic_analyzer.semantic_passes.error_handler import SemanticErrorHandler, ErrorCodes
from app.semantic_analyzer.builtin_recipes import get_builtin_recipe, is_builtin_recipe, find_compatible_builtin_overload
from typing import Optional, List


class FunctionChecker:
    """Performs recipe call checking on AST"""
    
    def __init__(self, symbol_table: SymbolTable, error_handler: SemanticErrorHandler):
        self.symbol_table = symbol_table
        self.error_handler = error_handler
    
    def check(self, ast_root: Program):
        """Run recipe checking pass"""
        # Check global declarations
        for decl in ast_root.global_decl:
            if isinstance(decl, IngrDecl) and decl.init_value:
                self._check_expression(decl.init_value)
            elif isinstance(decl, ArrayDecl) and decl.init_value:
                self._check_expression(decl.init_value)
            elif isinstance(decl, TableDecl) and decl.init_value:
                self._check_expression(decl.init_value)
        
        # Check recipe bodies
        for recipe in ast_root.recipe_decl:
            self._check_recipe_decl(recipe)
        
        # Check start_platter if present (navigate to its existing scope)
        if ast_root.start_platter:
            if self.symbol_table.navigate_to_scope("start_platter_1"):
                self._check_platter(ast_root.start_platter)
                self.symbol_table.exit_scope()
    
    def _check_recipe_decl(self, node: RecipeDecl):
        """Check recipe declaration"""
        # Check recipe body (navigate to existing recipe scope)
        if node.body:
            scope_name = node.name  # The builder removed 'recipe_' prefix
            if self.symbol_table.navigate_to_scope(scope_name):
                self._check_platter(node.body)
                self.symbol_table.exit_scope()
    
    def _check_platter(self, node: Platter):
        """Check block/compound statement"""
        # Check local declarations
        for decl in node.local_decls:
            if isinstance(decl, IngrDecl) and decl.init_value:
                self._check_expression(decl.init_value)
            elif isinstance(decl, ArrayDecl) and decl.init_value:
                self._check_expression(decl.init_value)
            elif isinstance(decl, TableDecl) and decl.init_value:
                self._check_expression(decl.init_value)
        
        # Check statements
        for stmt in node.statements:
            self._check_statement(stmt)
    
    def _check_statement(self, node: ASTNode):
        """Check a statement"""
        if isinstance(node, Assignment):
            self._check_expression(node.target)
            self._check_expression(node.value)
        elif isinstance(node, ServeStatement):
            if node.value:
                self._check_expression(node.value)
        elif isinstance(node, CheckStatement):
            self._check_expression(node.condition)
            self._check_platter(node.then_block)
            for elif_cond, elif_block in node.elif_clauses:
                self._check_expression(elif_cond)
                self._check_platter(elif_block)
            if node.else_block:
                self._check_platter(node.else_block)
        elif isinstance(node, MenuStatement):
            self._check_expression(node.expr)
            for case in node.cases:
                for value in case.values:
                    self._check_expression(value)
                for stmt in case.statements:
                    self._check_statement(stmt)
            if node.default:
                for stmt in node.default:
                    self._check_statement(stmt)
        elif isinstance(node, RepeatLoop):
            self._check_expression(node.condition)
            self._check_platter(node.body)
        elif isinstance(node, OrderRepeatLoop):
            self._check_platter(node.body)
            self._check_expression(node.condition)
        elif isinstance(node, PassLoop):
            if node.init:
                if isinstance(node.init, Assignment):
                    self._check_expression(node.init.target)
                    self._check_expression(node.init.value)
            if node.condition:
                self._check_expression(node.condition)
            if node.update:
                if isinstance(node.update, Assignment):
                    self._check_expression(node.update.target)
                    self._check_expression(node.update.value)
            self._check_platter(node.body)
        elif isinstance(node, Platter):
            self._check_platter(node)
        elif isinstance(node, ExpressionStatement):
            self._check_expression(node.expr)
    
    def _check_expression(self, expr: ASTNode):
        """Check expression for function calls"""
        if expr is None:
            return
        
        if isinstance(expr, RecipeCall):
            self._check_function_call(expr)
        elif isinstance(expr, BinaryOp):
            self._check_expression(expr.left)
            self._check_expression(expr.right)
        elif isinstance(expr, UnaryOp):
            self._check_expression(expr.operand)
        elif isinstance(expr, ArrayAccess):
            self._check_expression(expr.array)
            self._check_expression(expr.index)
        elif isinstance(expr, TableAccess):
            self._check_expression(expr.table)
        elif isinstance(expr, CastExpr):
            self._check_expression(expr.expr)
        elif isinstance(expr, ArrayLiteral):
            for elem in expr.elements:
                self._check_expression(elem)
        elif isinstance(expr, TableLiteral):
            for field_name, value, line, col in expr.field_inits:
                self._check_expression(value)
    
    def _check_function_call(self, node: RecipeCall):
        """Check recipe call flavors (arguments)"""
        # Check if it's a built-in recipe
        if is_builtin_recipe(node.name):
            # Get argument types to find the matching overload
            arg_types = []
            for arg in node.args:
                arg_type = self._get_expression_type(arg)
                if arg_type:
                    arg_types.append((arg_type.base_type, arg_type.dimensions))
                else:
                    # Can't determine arg type, but still check arguments recursively
                    for arg in node.args:
                        self._check_expression(arg)
                    return
            
            # Find matching overload
            builtin_overload = find_compatible_builtin_overload(node.name, arg_types)
            if builtin_overload:
                self._check_builtin_recipe_call(node, builtin_overload)
            else:
                # No matching overload - report error
                self.error_handler.add_error(
                    f"No matching overload for built-in recipe '{node.name}' with argument types: {arg_types}",
                    node,
                    ErrorCodes.FLAVOR_TYPE_MISMATCH
                )
            
            # Still recursively check flavors
            for arg in node.args:
                self._check_expression(arg)
            return
        
        # Look up recipe symbol
        recipe_symbol = self.symbol_table.lookup_symbol(node.name)
        if not recipe_symbol:
            # Error already reported by scope_checker
            return
        
        if recipe_symbol.kind != SymbolKind.FUNCTION:
            # Error already reported by scope_checker
            return
        
        # Get recipe spices (parameters)
        spices = self._get_recipe_spices(node.name)
        if spices is None:
            # Could not determine spices
            return
        
        # Check flavor count
        if len(node.args) != len(spices):
            self.error_handler.add_error(
                f"Recipe '{node.name}' expects {len(spices)} flavor(s), got {len(node.args)}",
                node,
                ErrorCodes.FLAVOR_COUNT_MISMATCH
            )
            return
        
        # Check flavor types
        for i, (arg, spice) in enumerate(zip(node.args, spices)):
            arg_type = self._get_expression_type(arg)
            spice_type = spice.type_info
            
            if arg_type and not spice_type.is_compatible_with(arg_type):
                self.error_handler.add_error(
                    f"Flavor {i+1} of recipe '{node.name}': "
                    f"expected {spice_type}, got {arg_type}",
                    arg,
                    ErrorCodes.FLAVOR_TYPE_MISMATCH
                )
        
        # Recursively check flavors
        for arg in node.args:
            self._check_expression(arg)
    
    def _check_builtin_recipe_call(self, node: RecipeCall, builtin):
        """Check built-in recipe call"""
        expected_count = builtin.get_spice_count()
        
        # Check flavor count
        if len(node.args) != expected_count:
            self.error_handler.add_error(
                f"Built-in recipe '{node.name}' expects {expected_count} flavor(s), got {len(node.args)}",
                node,
                ErrorCodes.FLAVOR_COUNT_MISMATCH
            )
            return
        
        # Check flavor types (with flexible type checking for built-ins)
        for i, arg in enumerate(node.args):
            arg_type = self._get_expression_type(arg)
            expected_spice_type = builtin.get_spice_type_info(i)
            
            if arg_type and expected_spice_type:
                # For built-ins, be more flexible with type compatibility
                if not self._is_compatible_for_builtin(arg_type, expected_spice_type):
                    self.error_handler.add_error(
                        f"Flavor {i+1} of built-in recipe '{node.name}': "
                        f"expected {expected_spice_type}, got {arg_type}",
                        arg,
                        ErrorCodes.FLAVOR_TYPE_MISMATCH
                    )
    
    def _is_compatible_for_builtin(self, arg_type: TypeInfo, expected_type: TypeInfo) -> bool:
        """Check if a type is compatible for built-in recipe calls (more flexible)"""
        # First check with standard compatibility
        if expected_type.is_compatible_with(arg_type):
            return True
        
        # For built-ins, allow any scalar type to be converted
        if expected_type.dimensions == 0 and arg_type.dimensions == 0:
            # Allow piece/sip/chars/flag to be compatible with each other for built-ins
            return True
        
        # Check if dimensions match (important for array operations)
        return expected_type.dimensions == arg_type.dimensions
    
    def _get_recipe_spices(self, recipe_name: str) -> Optional[List[Symbol]]:
        """Get recipe spices (parameters) from the AST or symbol table"""
        # Look up the recipe symbol
        recipe_symbol = self.symbol_table.lookup_symbol(recipe_name)
        if not recipe_symbol or recipe_symbol.kind != SymbolKind.FUNCTION:
            return None
        
        # Find the recipe's scope
        recipe_scope = None
        for child in self.symbol_table.global_scope.children:
            if child.name == recipe_name:
                recipe_scope = child
                break
        
        if not recipe_scope:
            return None
        
        # Get spices (symbols with kind PARAMETER)
        spices = []
        for name, symbol in recipe_scope.symbols.items():
            if symbol.kind == SymbolKind.PARAMETER:
                spices.append(symbol)
        
        return spices
    
    def _get_expression_type(self, expr: ASTNode) -> Optional[TypeInfo]:
        """Get the type of an expression (simplified version)"""
        if expr is None:
            return None
        
        if isinstance(expr, Literal):
            return TypeInfo(expr.value_type, 0)
        
        elif isinstance(expr, Identifier):
            symbol = self.symbol_table.lookup_symbol(expr.name)
            if symbol:
                return symbol.type_info
            return None
        
        elif isinstance(expr, BinaryOp):
            left_type = self._get_expression_type(expr.left)
            if expr.operator in ['==', '!=', '<', '>', '<=', '>=', '&&', '||']:
                return TypeInfo("flag", 0)
            return left_type
        
        elif isinstance(expr, UnaryOp):
            if expr.operator == '!':
                return TypeInfo("flag", 0)
            return self._get_expression_type(expr.operand)
        
        elif isinstance(expr, ArrayAccess):
            array_type = self._get_expression_type(expr.array)
            if array_type and array_type.dimensions > 0:
                return array_type.get_element_type()
            return None
        
        elif isinstance(expr, TableAccess):
            table_type = self._get_expression_type(expr.table)
            if table_type and table_type.is_table:
                return table_type.get_field_type(expr.field)
            return None
        
        elif isinstance(expr, RecipeCall):
            func_symbol = self.symbol_table.lookup_symbol(expr.name)
            if func_symbol:
                return func_symbol.type_info
            return None
        
        elif isinstance(expr, CastExpr):
            dims = expr.dimensions if expr.dimensions is not None else 0
            return TypeInfo(expr.target_type, dims)
        
        elif isinstance(expr, ArrayLiteral):
            if expr.elements:
                first_type = self._get_expression_type(expr.elements[0])
                if first_type:
                    return TypeInfo(first_type.base_type, first_type.dimensions + 1, 
                                  first_type.table_fields if first_type.is_table else None)
            return None
        
        elif isinstance(expr, TableLiteral):
            # Build field types from literal
            field_types = {}
            for field_name, value, line, col in expr.field_inits:
                field_type = self._get_expression_type(value)
                if field_type:
                    field_types[field_name] = field_type
            return TypeInfo("anonymous_table", 0, field_types)
        
        return None
