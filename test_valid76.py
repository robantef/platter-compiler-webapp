import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'platter-compiler-sveltejs' / 'static' / 'python'))

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from app.semantic_analyzer.ast.ast_nodes import Assignment, RecipeCall
from app.parser.parser_program import Parser

file_path = Path('platter-compiler-sveltejs/static/python/tests/semantic_programs/source_code/test_valid76.platter')
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

print("=== test_valid76.platter ===")
print(code)
print()

lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
parser.parse_program()

ast_parser = ASTParser(tokens)
ast = ast_parser.parse_program()

# Debug the AST
print("=== AST DEBUG ===")
if ast.start_platter:
    for stmt in ast.start_platter.statements:
        if isinstance(stmt, Assignment):
            print(f"Assignment: {stmt}")
            print(f"  Target: {stmt.target} (type: {type(stmt.target).__name__})")
            print(f"  Value: {stmt.value} (type: {type(stmt.value).__name__})")
            if isinstance(stmt.value, RecipeCall):
                print(f"    Recipe: {stmt.value.name}")
                print(f"    Args: {stmt.value.args}")
                for i, arg in enumerate(stmt.value.args):
                    print(f"      Arg {i}: {arg} (type: {type(arg).__name__})")
                    if hasattr(arg, 'array') and hasattr(arg, 'index'):
                        print(f"        Array: {arg.array}")
                        print(f"        Index: {arg.index}")
print()

analyzer = SemanticAnalyzer()
symbol_table, error_handler = analyzer.analyze(ast)

if error_handler.has_errors() or error_handler.has_warnings():
    actual = error_handler.format_errors(include_warnings=True, include_info=False)
    print("Errors/Warnings:")
    print(actual)
else:
    print("No semantic errors")
