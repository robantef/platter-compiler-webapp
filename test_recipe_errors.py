import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'platter-compiler-sveltejs' / 'static' / 'python'))

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from app.parser.parser_program import Parser

def test_file(filename, description):
    print(f"\n{'='*70}")
    print(f"Testing: {filename}")
    print(f"Description: {description}")
    print('='*70)
    
    file_path = Path(f'platter-compiler-sveltejs/static/python/tests/semantic_programs/source_code/{filename}')
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    print("\nSource code:")
    print(code)
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    parser.parse_program()
    
    ast_parser = ASTParser(tokens)
    ast = ast_parser.parse_program()
    
    analyzer = SemanticAnalyzer()
    try:
        symbol_table, error_handler = analyzer.analyze(ast)
    except Exception as e:
        import traceback
        print("\nException during semantic analysis:")
        traceback.print_exc()
        return
    
    if error_handler.has_errors() or error_handler.has_warnings():
        actual = error_handler.format_errors(include_warnings=True, include_info=False)
        print("\nActual output:")
        print(actual)
    else:
        print("\nNo semantic errors")

# Test all failing cases
test_file("ts_invalid21.platter", "Check statement with non-flag condition")
test_file("ts_invalid86.platter", "Check statement with piece condition")
test_file("ts_invalid61.platter", "Menu with duplicate choice values")
test_file("ts_invalid79.platter", "Recipe parameter type mismatch")
test_file("ts_invalid80.platter", "Recipe/ingredient shadowing issue")
