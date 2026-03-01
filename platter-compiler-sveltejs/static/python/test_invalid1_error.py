"""
Test script to check error message for test_invalid1.platter
"""

from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

# Test program
test_program = """chars[] of names = [[],[]];
start() {  }"""

print("Testing: test_invalid1.platter")
print("-" * 60)

# Lexical and syntax analysis
lexer = Lexer(test_program)
tokens = lexer.tokenize()

try:
    parser = Parser(tokens)
    parser.parse_program()
except Exception as e:
    print(f"Syntax error: {e}")
    exit(1)

# Semantic analysis
ast_parser = ASTParser(tokens)
ast = ast_parser.parse_program()
analyzer = SemanticAnalyzer()
symbol_table, error_handler = analyzer.analyze(ast)

# Output errors
if error_handler.has_errors() or error_handler.has_warnings():
    output = error_handler.format_errors(include_warnings=True, include_info=False)
    print("\nError output:")
    print(output)
else:
    print("\nNo semantic errors")
