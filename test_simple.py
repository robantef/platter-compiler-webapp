"""Simple test for PassLoop"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'platter-compiler-sveltejs', 'static', 'python')))

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

source_code = """
start() {
    pass (i = 0; i += 1; (i > 4)) {
    }
}
"""

print("Parsing...")
lexer = Lexer(source_code)
tokens = lexer.tokenize()
parser = ASTParser(tokens)
ast = parser.parse_program()

print("Running semantic analysis...")
try:
    analyzer = SemanticAnalyzer()
    symbol_table, error_handler = analyzer.analyze(ast)
    print(f"Analysis completed. Errors: {error_handler.get_error_count()}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
