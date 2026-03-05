import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'platter-compiler-sveltejs' / 'static' / 'python'))

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

file_path = Path('platter-compiler-sveltejs/static/python/tests/semantic_programs/source_code/ts_invalid44.platter')
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

print("=== ts_invalid44.platter ===")
print(code)
print()

lexer = Lexer(code)
tokens = lexer.tokenize()

ast_parser = ASTParser(tokens)
ast = ast_parser.parse_program()

analyzer = SemanticAnalyzer()
symbol_table, error_handler = analyzer.analyze(ast)

if error_handler.has_errors() or error_handler.has_warnings():
    actual = error_handler.format_errors(include_warnings=True, include_info=False)
    print(actual)
else:
    print('No semantic errors')
