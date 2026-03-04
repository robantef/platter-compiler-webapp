"""
Test for PassLoop undefined variable detection
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'platter-compiler-sveltejs', 'static', 'python')))

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

# Test case: undefined variable 'i' in pass loop
source_code = """
start() {
    pass (i = 0; i += 1; (i > 4)) {
    }
}
"""

print("Testing undefined variable in pass loop...")
print("Source code:")
print(source_code)
print("\n" + "="*60 + "\n")

# Lex and parse
lexer = Lexer(source_code)
tokens = lexer.tokenize()
parser = ASTParser(tokens)
ast = parser.parse_program()

# Run semantic analysis
analyzer = SemanticAnalyzer()
symbol_table, error_handler = analyzer.analyze(ast)

# Print results
print("Semantic Analysis Results:")
print(f"Errors: {error_handler.get_error_count()}")
print(f"Warnings: {error_handler.get_warning_count()}")
print()

if error_handler.has_errors():
    print("ERRORS DETECTED:")
    print(error_handler.format_errors(include_warnings=False))
else:
    print("NO ERRORS DETECTED - THIS IS A BUG!")
    
print("\n" + "="*60 + "\n")
print("Expected: Error about undefined ingredient 'i'")
print(f"Actual: {error_handler.get_error_count()} error(s)")
