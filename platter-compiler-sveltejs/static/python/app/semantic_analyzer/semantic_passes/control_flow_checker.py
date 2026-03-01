"""
Control Flow Checking Pass for Platter Language
Validates control flow statements (break, continue, return)
"""

from app.semantic_analyzer.ast.ast_nodes import *
from app.semantic_analyzer.symbol_table.symbol_table import SymbolTable
from app.semantic_analyzer.semantic_passes.error_handler import SemanticErrorHandler, ErrorCodes


class ControlFlowChecker:
    """Performs control flow checking on AST"""
    
    def __init__(self, symbol_table: SymbolTable, error_handler: SemanticErrorHandler):
        self.symbol_table = symbol_table
        self.error_handler = error_handler
        self.in_loop = 0
        self.in_recipe = False
        self.current_recipe_has_serve = False
        self.code_is_reachable = True  # Track if current code is reachable
    
    def check(self, ast_root: Program):
        """Run control flow checking pass"""
        # Check recipe bodies
        for recipe in ast_root.recipe_decl:
            self._check_recipe_decl(recipe)
        
        # Check start_platter if present (treat as a recipe)
        if ast_root.start_platter:
            old_in_recipe = self.in_recipe
            self.in_recipe = True
            self._check_platter(ast_root.start_platter)
            self.in_recipe = old_in_recipe
    
    def _check_recipe_decl(self, node: RecipeDecl):
        """Check recipe declaration"""
        old_in_recipe = self.in_recipe
        old_has_serve = self.current_recipe_has_serve
        
        self.in_recipe = True
        self.current_recipe_has_serve = False
        
        # Check recipe body
        if node.body:
            self._check_platter(node.body)
        
        # Check if non-void recipe has guaranteed serve statement
        if node.return_type != "void":
            if not node.body or not self._block_has_serve(node.body):
                self.error_handler.add_error(
                    f"Recipe '{node.name}' must have a guaranteed serve statement in all code paths",
                    node,
                    ErrorCodes.MISSING_SERVE
                )
        
        self.in_recipe = old_in_recipe
        self.current_recipe_has_serve = old_has_serve
    
    def _check_platter(self, node: Platter):
        """Check block/compound statement"""
        for i, stmt in enumerate(node.statements):
            self._check_statement(stmt)
            
            # If we hit a serve statement, mark subsequent code as unreachable
            if isinstance(stmt, ServeStatement):
                # Check if there are statements after serve
                if i + 1 < len(node.statements):
                    next_stmt = node.statements[i + 1]
                    self.error_handler.add_error(
                        "Unreachable code after serve statement",
                        next_stmt,
                        ErrorCodes.UNREACHABLE_CODE
                    )
                    break  # Stop checking further statements in this block
    
    def _check_statement(self, node: ASTNode):
        """Check a statement"""
        if isinstance(node, BreakStatement):
            self._check_break_statement(node)
        elif isinstance(node, ContinueStatement):
            self._check_continue_statement(node)
        elif isinstance(node, ServeStatement):
            self._check_serve_statement(node)
        elif isinstance(node, CheckStatement):
            self._check_check_statement(node)
        elif isinstance(node, MenuStatement):
            self._check_menu_statement(node)
        elif isinstance(node, RepeatLoop):
            self._check_repeat_loop(node)
        elif isinstance(node, OrderRepeatLoop):
            self._check_order_repeat_loop(node)
        elif isinstance(node, PassLoop):
            self._check_pass_loop(node)
        elif isinstance(node, Platter):
            self._check_platter(node)
    
    def _check_break_statement(self, node: BreakStatement):
        """Check stop statement is inside a loop or menu"""
        if self.in_loop == 0:
            self.error_handler.add_error(
                "stop statement outside of loop",
                node,
                ErrorCodes.STOP_OUTSIDE_LOOP
            )
    
    def _check_continue_statement(self, node: ContinueStatement):
        """Check next statement is inside a loop"""
        if self.in_loop == 0:
            self.error_handler.add_error(
                "next statement outside of loop",
                node,
                ErrorCodes.NEXT_OUTSIDE_LOOP
            )
    
    def _check_serve_statement(self, node: ServeStatement):
        """Check serve statement is inside a recipe"""
        if not self.in_recipe:
            self.error_handler.add_error(
                "serve statement outside of recipe",
                node,
                ErrorCodes.SERVE_OUTSIDE_RECIPE
            )
    
    def _check_check_statement(self, node: CheckStatement):
        """Check check statement (if/alt/instead)"""
        # Check branches
        self._check_platter(node.then_block)
        for _, alt_block in node.elif_clauses:
            self._check_platter(alt_block)
        if node.else_block:
            self._check_platter(node.else_block)
    
    def _check_menu_statement(self, node: MenuStatement):
        """Check menu statement (menu/choice/usual)"""
        # Allow stop in menu
        self.in_loop += 1
        
        # Check choices
        for case in node.cases:
            for stmt in case.statements:
                self._check_statement(stmt)
        
        # Check usual case
        if node.default:
            for stmt in node.default:
                self._check_statement(stmt)
        
        self.in_loop -= 1
    
    def _check_repeat_loop(self, node: RepeatLoop):
        """Check repeat loop"""
        self.in_loop += 1
        self._check_platter(node.body)
        self.in_loop -= 1
    
    def _check_order_repeat_loop(self, node: OrderRepeatLoop):
        """Check order-repeat loop"""
        self.in_loop += 1
        self._check_platter(node.body)
        self.in_loop -= 1
    
    def _check_pass_loop(self, node: PassLoop):
        """Check pass loop"""
        self.in_loop += 1
        self._check_platter(node.body)
        self.in_loop -= 1
    
    def _block_has_serve(self, block: Platter) -> bool:
        """Check if a block definitely has a serve statement"""
        for stmt in block.statements:
            if isinstance(stmt, ServeStatement):
                return True
            elif isinstance(stmt, CheckStatement):
                # Check if all branches serve
                then_serves = self._block_has_serve(stmt.then_block)
                
                alt_serves = []
                for _, alt_block in stmt.elif_clauses:
                    alt_serves.append(self._block_has_serve(alt_block))
                
                instead_serves = False
                if stmt.else_block:
                    instead_serves = self._block_has_serve(stmt.else_block)
                
                if then_serves and (not stmt.elif_clauses or all(alt_serves)) and instead_serves:
                    return True
        
        return False
