import sys
import logging
sys.path.insert(0, 'd:\\Repositories\\platter-compiler-webapp\\platter-compiler-sveltejs\\static\\python')

# Suppress debug logs
logging.getLogger().setLevel(logging.CRITICAL)

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

def test_file(name, filepath):
    print(f"\n{'='*60}")
    print(f"Testing {name}")
    print('='*60)
    try:
        with open(filepath, 'r') as file:
            program_text = file.read()
        
        print(f"Code:\n{program_text}\n")
        
        # Lex and build AST
        lexer = Lexer(program_text)
        tokens = lexer.tokenize()
        
        ast_parser = ASTParser(tokens)
        ast = ast_parser.parse_program()
        
        # Semantic analysis
        analyzer = SemanticAnalyzer()
        symbol_table, error_handler = analyzer.analyze(ast)
        
        # Print results
        print("Result:")
        if error_handler.has_errors() or error_handler.has_warnings():
            print(error_handler.format_errors(include_warnings=True, include_info=False))
        else:
            print("No semantic errors")
            
        return True
    except Exception as e:
        print(f"CRASH: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test all recipe error files
basepath = 'd:\\Repositories\\platter-compiler-webapp\\platter-compiler-sveltejs\\static\\python\\tests\\semantic_programs\\source_code\\'
test_file('ts_invalid21 - Check statement type', basepath + 'ts_invalid21.platter')
test_file('ts_invalid61 - Menu duplicate choice', basepath + 'ts_invalid61.platter')
test_file('ts_invalid79 - Recipe parameter type', basepath + 'ts_invalid79.platter')
test_file('ts_invalid80 - Recipe shadowing', basepath + 'ts_invalid80.platter')
test_file('ts_invalid86 - Check with piece condition', basepath + 'ts_invalid86.platter')
