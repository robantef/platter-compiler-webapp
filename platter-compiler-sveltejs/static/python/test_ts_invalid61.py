import sys
import logging
sys.path.insert(0, 'd:\\Repositories\\platter-compiler-webapp\\platter-compiler-sveltejs\\static\\python')

# Suppress debug logs
logging.getLogger().setLevel(logging.CRITICAL)

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from app.parser.parser_program import Parser

def test_file(filepath):
    print(f"\n=== Testing {filepath} ===")
    try:
        with open(filepath, 'r') as file:
            program_text = file.read()
        
        print(f"Program:\n{program_text}\n")
        
        # Lex and build AST
        lexer = Lexer(program_text)
        tokens = lexer.tokenize()
        
        ast_parser = ASTParser(tokens)
        ast = ast_parser.parse_program()
        
        # Semantic analysis
        analyzer = SemanticAnalyzer()
        symbol_table, error_handler = analyzer.analyze(ast)
        
        # Print results
        if error_handler.has_errors() or error_handler.has_warnings():
            print("Errors/Warnings:")
            print(error_handler.format_errors(include_warnings=True, include_info=False))
        else:
            print("No semantic errors")
            
        return True
    except Exception as e:
        print(f"CRASH: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test the file
test_file('d:\\Repositories\\platter-compiler-webapp\\platter-compiler-sveltejs\\static\\python\\tests\\semantic_programs\\source_code\\ts_invalid61.platter')
