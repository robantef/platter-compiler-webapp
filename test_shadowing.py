"""Test shadowing detection"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'platter-compiler-sveltejs', 'static', 'python')))

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

code = """
piece of c = 1;

start(){
    piece of a = 5;
    piece of b = c;
    piece of c = 1;
}
"""

lexer = Lexer(code)
tokens = lexer.tokenize()
parser = ASTParser(tokens)
ast = parser.parse_program()
analyzer = SemanticAnalyzer()
symbol_table, error_handler = analyzer.analyze(ast)

print(f"Errors: {error_handler.get_error_count()}")
if error_handler.has_errors():
    for error in error_handler.errors:
        print(f"  - {error.message}")
else:
    print("No errors - BUG: should detect shadowing!")
