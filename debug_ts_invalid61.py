import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'platter-compiler-sveltejs' / 'static' / 'python'))

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.parser.parser_program import Parser

file_path = Path('platter-compiler-sveltejs/static/python/tests/semantic_programs/source_code/ts_invalid61.platter')
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

print("Source:")
print(code)
print()

lexer = Lexer(code)
tokens = lexer.tokenize()

parser = Parser(tokens)
parser.parse_program()

ast_parser = ASTParser(tokens)
ast = ast_parser.parse_program()

# Check the AST structure
if ast.start_platter:
    for stmt in ast.start_platter.statements:
        print(f"Statement: {stmt}")
        if hasattr(stmt, 'cases'):
            print(f"  Cases: {stmt.cases}")
            for case in stmt.cases:
                print(f"    Case: {case}")
                print(f"      value attribute: {hasattr(case, 'value')}")
                print(f"      values attribute: {hasattr(case, 'values')}")
                if hasattr(case, 'value'):
                    print(f"      case.value = {case.value} (type: {type(case.value)})")
                if hasattr(case, 'values'):
                    print(f"      case.values = {case.values} (type: {type(case.values)})")
