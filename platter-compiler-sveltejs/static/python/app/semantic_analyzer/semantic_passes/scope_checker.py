"""
Scope Checking Pass for Platter Language
Validates symbol declarations, definitions, and usage
"""

from app.semantic_analyzer.ast.ast_nodes import *
from app.semantic_analyzer.symbol_table.types import Symbol, SymbolKind
from app.semantic_analyzer.symbol_table.symbol_table import SymbolTable
from app.semantic_analyzer.semantic_passes.error_handler import SemanticErrorHandler, ErrorCodes
from app.semantic_analyzer.builtin_recipes import is_builtin_recipe
from typing import Set


class ScopeChecker:
    """Performs scope checking on AST"""
    
    def __init__(self, symbol_table: SymbolTable, error_handler: SemanticErrorHandler):
        self.symbol_table = symbol_table
        self.error_handler = error_handler
        self.used_symbols: Set[str] = set()
    
    def check(self, ast_root: Program):
        """Run scope checking pass"""
        # Check for undefined symbols in expressions
        for decl in ast_root.global_decl:
            if isinstance(decl, IngrDecl):
                self._check_var_decl(decl)
            elif isinstance(decl, ArrayDecl):
                self._check_array_decl(decl)
            elif isinstance(decl, TableDecl):
                self._check_table_decl(decl)
        
        # Check function bodies
        for recipe in ast_root.recipe_decl:
            self._check_recipe_decl(recipe)
        
        # Check start_platter if present (navigate to its existing scope)
        if ast_root.start_platter:
            if self.symbol_table.navigate_to_scope("start_platter_1"):
                self._check_platter(ast_root.start_platter)
                self.symbol_table.exit_scope()
        
        # Check for unused ingredients (warnings)
        self._check_unused_symbols()
    
    def _check_var_decl(self, node: IngrDecl):
        """Check ingredient declaration"""
        # Check if type is defined
        if not self.symbol_table.is_type_defined(node.data_type):
            self.error_handler.add_error(
                f"Undefined type '{node.data_type}'",
                node,
                ErrorCodes.UNDEFINED_TYPE
            )
        
        # Check initialization expression
        if node.init_value:
            self._check_expression(node.init_value)
    
    def _check_array_decl(self, node: ArrayDecl):
        """Check array declaration"""
        # Check if type is defined
        if not self.symbol_table.is_type_defined(node.data_type):
            self.error_handler.add_error(
                f"Undefined type '{node.data_type}'",
                node,
                ErrorCodes.UNDEFINED_TYPE
            )
        
        # Check dimensions
        if node.dimensions is not None and node.dimensions <= 0:
            self.error_handler.add_error(
                f"Array dimensions must be positive, got {node.dimensions}",
                node,
                ErrorCodes.INVALID_DIMENSION
            )
        
        # Check initialization expression
        if node.init_value:
            self._check_expression(node.init_value)
    
    def _check_table_decl(self, node: TableDecl):
        """Check table declaration"""
        # Check if table type is defined
        if not self.symbol_table.lookup_table_type(node.table_type):
            self.error_handler.add_error(
                f"Undefined table type '{node.table_type}'",
                node,
                ErrorCodes.UNDEFINED_TYPE
            )
        
        # Check dimensions if it's an array of tables
        if node.dimensions is not None and node.dimensions < 0:
            self.error_handler.add_error(
                f"Array dimensions must be positive, got {node.dimensions}",
                node,
                ErrorCodes.INVALID_DIMENSION
            )
        
        # Check initialization expression
        if node.init_value:
            self._check_expression(node.init_value)
    
    def _check_recipe_decl(self, node: RecipeDecl):
        """Check recipe declaration"""
        # Check serve type
        if not self.symbol_table.is_type_defined(node.return_type):
            self.error_handler.add_error(
                f"Undefined serve type '{node.return_type}'",
                node,
                ErrorCodes.UNDEFINED_TYPE
            )
        
        # Check spice types
        for spice in node.params:
            if not self.symbol_table.is_type_defined(spice.data_type):
                self.error_handler.add_error(
                    f"Undefined spice type '{spice.data_type}' in spice '{spice.identifier}'",
                    spice,
                    ErrorCodes.UNDEFINED_TYPE
                )
        
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
            if isinstance(decl, IngrDecl):
                self._check_var_decl(decl)
            elif isinstance(decl, ArrayDecl):
                self._check_array_decl(decl)
            elif isinstance(decl, TableDecl):
                self._check_table_decl(decl)
        
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
        """Check expression for undefined symbols"""
        if expr is None:
            return
        
        if isinstance(expr, Identifier):
            # Check if symbol is defined
            symbol = self.symbol_table.lookup_symbol(expr.name)
            if not symbol:
                scope_name = self.symbol_table.current_scope.name
                self.error_handler.add_error(
                    f"Undefined ingredient '{expr.name}' in '{scope_name}'",
                    expr,
                    ErrorCodes.UNDEFINED_SYMBOL
                )
            else:
                # Mark symbol as used
                self.used_symbols.add(expr.name)
        
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
        
        elif isinstance(expr, RecipeCall):
            # Check if recipe is defined (including built-in recipes)
            if is_builtin_recipe(expr.name):
                # Built-in recipes are always available
                self.used_symbols.add(expr.name)
            else:
                recipe_symbol = self.symbol_table.lookup_symbol(expr.name)
                if not recipe_symbol:
                    scope_name = self.symbol_table.current_scope.name
                    self.error_handler.add_error(
                        f"Undefined recipe '{expr.name}' in '{scope_name}'",
                        expr,
                        ErrorCodes.UNDEFINED_RECIPE
                    )
                elif recipe_symbol.kind != SymbolKind.FUNCTION:
                    self.error_handler.add_error(
                        f"'{expr.name}' is not a recipe",
                        expr,
                        ErrorCodes.UNDEFINED_RECIPE
                    )
                else:
                    # Mark recipe as used
                    self.used_symbols.add(expr.name)
            
            # Check flavors (arguments)
            for arg in expr.args:
                self._check_expression(arg)
        
        elif isinstance(expr, CastExpr):
            # Check target type is defined
            if not self.symbol_table.is_type_defined(expr.target_type):
                self.error_handler.add_error(
                    f"Undefined type '{expr.target_type}' in cast",
                    expr,
                    ErrorCodes.UNDEFINED_TYPE
                )
            self._check_expression(expr.expr)
        
        elif isinstance(expr, ArrayLiteral):
            for elem in expr.elements:
                self._check_expression(elem)
        
        elif isinstance(expr, TableLiteral):
            for field_name, value, line, col in expr.field_inits:
                self._check_expression(value)
    
    def _check_unused_symbols(self):
        """Check for unused ingredients and issue warnings"""
        # Recursively check all scopes
        self._check_scope_for_unused(self.symbol_table.global_scope)
    
    def _check_scope_for_unused(self, scope):
        """Recursively check scope and children for unused symbols"""
        for name, symbol in scope.symbols.items():
            # Skip functions and table types
            if symbol.kind in [SymbolKind.FUNCTION, SymbolKind.TABLE_TYPE]:
                continue
            
            # Check if symbol was used
            if name not in self.used_symbols:
                self.error_handler.add_warning(
                    f"Unused ingredient '{name}'",
                    symbol.declaration_node,
                    ErrorCodes.UNUSED_INGREDIENT
                )
        
        # Check child scopes
        for child in scope.children:
            self._check_scope_for_unused(child)
