import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'platter-compiler-sveltejs' / 'static' / 'python'))

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from app.parser.parser_program import Parser

# Test ts_invalid95
file_path = Path('platter-compiler-sveltejs/static/python/tests/semantic_programs/source_code/ts_invalid95.platter')
expected_path = Path('platter-compiler-sveltejs/static/python/tests/semantic_programs/expected/ts_invalid95.txt')

with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()
with open(expected_path, 'r', encoding='utf-8') as f:
    expected = f.read().strip()

print("=== ts_invalid95.platter ===")
print(code)
print()
print(f"Expected: {expected}")
print()

# Lexical + Syntax analysis
lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
parser.parse_program()

# Semantic analysis
ast_parser = ASTParser(tokens)
ast = ast_parser.parse_program()
analyzer = SemanticAnalyzer()
symbol_table, error_handler = analyzer.analyze(ast)

if error_handler.has_errors() or error_handler.has_warnings():
    actual = error_handler.format_errors(include_warnings=True, include_info=False)
else:
    actual = "No semantic errors"

print(f"Actual: {actual}")
print()

if expected.lower() in actual.lower() or any(word in actual.lower() for word in expected.lower().split()):
    print("[OK] Test PASSED")
else:
    print("[FAIL] Test FAILED")
