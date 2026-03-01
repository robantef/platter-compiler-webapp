"""
Main Semantic Analyzer for Platter Language
Coordinates all semantic analysis passes
"""

from app.semantic_analyzer.ast.ast_nodes import Program
from app.semantic_analyzer.symbol_table import SymbolTable, SymbolTableBuilder
from app.semantic_analyzer.semantic_passes import (
    SemanticErrorHandler,
    TypeChecker,
    ScopeChecker,
    ControlFlowChecker,
    FunctionChecker
)


class SemanticAnalyzer:
    """Main semantic analyzer that runs all passes"""
    
    def __init__(self):
        self.symbol_table = None
        self.error_handler = SemanticErrorHandler()
    
    def analyze(self, ast_root: Program) -> tuple[SymbolTable, SemanticErrorHandler]:
        """
        Perform complete semantic analysis on AST
        
        Returns:
            tuple: (symbol_table, error_handler)
        """
        # Phase 1: Build symbol table (collect symbols only)
        builder = SymbolTableBuilder()
        # Attach error handler before building
        builder.symbol_table.error_handler = self.error_handler
        self.symbol_table = builder.build(ast_root)
        
        # Phase 2: Run semantic checking passes
        self._run_semantic_passes(ast_root)
        
        return self.symbol_table, self.error_handler
    
    def _run_semantic_passes(self, ast_root: Program):
        """Run all semantic checking passes in order"""
        
        # Pass 1: Scope checking (undefined symbols, duplicate definitions)
        scope_checker = ScopeChecker(self.symbol_table, self.error_handler)
        scope_checker.check(ast_root)
        
        # Pass 2: Type checking (type compatibility, operations)
        type_checker = TypeChecker(self.symbol_table, self.error_handler)
        type_checker.check(ast_root)
        
        # Pass 3: Control flow checking (stop/next, serve statements)
        control_flow_checker = ControlFlowChecker(self.symbol_table, self.error_handler)
        control_flow_checker.check(ast_root)
        
        # Pass 4: Recipe checking (flavor count, flavor types)
        recipe_checker = FunctionChecker(self.symbol_table, self.error_handler)
        recipe_checker.check(ast_root)
    
    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return self.error_handler.has_errors()
    
    def get_error_count(self) -> int:
        """Get number of errors"""
        return self.error_handler.get_error_count()
    
    def get_warning_count(self) -> int:
        """Get number of warnings"""
        return self.error_handler.get_warning_count()
    
    def print_errors(self):
        """Print all errors and warnings"""
        print(self.error_handler.format_errors(include_warnings=True))
    
    def print_summary(self):
        """Print analysis summary"""
        self.error_handler.print_summary()


def analyze_program(ast_root: Program) -> tuple[SymbolTable, SemanticErrorHandler]:
    """
    Convenience function to analyze a program
    
    Args:
        ast_root: The root Program node of the AST
    
    Returns:
        tuple: (symbol_table, error_handler)
    """
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(ast_root)
