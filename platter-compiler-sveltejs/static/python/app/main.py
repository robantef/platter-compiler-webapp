from pprint import pprint

import logging as log
import subprocess
import sys
from app.lexer.token import Token
from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.ast.ast_reader import print_ast
from app.semantic_analyzer import analyze_program
from app.semantic_analyzer.symbol_table import print_symbol_table

COPY_ERROR_TO_CLIPBOARD = True


def set_clipboard(text):
    if not COPY_ERROR_TO_CLIPBOARD:
        return
    try: subprocess.run('clip', input=text.encode('utf-16le'), check=True, shell=True)
    except Exception:
        pass  

if __name__ == "__main__":
    filepath = sys.argv[1]
    include_whitespace = False 


    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    tokens = [
        t for t in tokens
        if t.type not in ("comment", "space", "newline", "tab") or include_whitespace
    ]
    
    try:
        print("=" * 80)
        print("\n\nLEXICAL:")
        pprint(tokens)
        print((" ".join(t.type for t in tokens if not "comment" in t.type )))
        set_clipboard((" ".join(t.type for t in tokens if not "comment" in t.type )))   
        
        
        print("=" * 80)
        print("\n\nSYNTAX:")
        log.disable(log.WARNING) 
        parser = Parser(tokens)
        python_error = None
        try:
            parser.parse_program()
            python_error = "No Syntax Error"
            print(python_error)
        except SyntaxError as e:
            python_error = str(e)
            print(python_error)

            
        print("=" * 80)
        print("\n\nSEMANTIC ANALYSIS:")
        
        # Disable all logging for semantic analysis in this file only
        log.disable(log.CRITICAL)
        
        try:
            # Parse AST
            ast_parser = ASTParser(tokens)
            ast = ast_parser.parse_program()
            
            # Run semantic analysis
            symbol_table, error_handler = analyze_program(ast)
            
            # Print AST Structure (capture and filter output)
            print("\nAST Structure:")
            import io
            from contextlib import redirect_stdout
            
            ast_buffer = io.StringIO()
            with redirect_stdout(ast_buffer):
                print_ast(ast, format="pretty")
            print(ast_buffer.getvalue())
            
            # Print Symbol Table (capture and filter output)
            print("\nSymbol Table:")
            symbol_buffer = io.StringIO()
            with redirect_stdout(symbol_buffer):
                print_symbol_table(symbol_table, error_handler)
            
            # Filter out unwanted sections and fix border characters
            symbol_output = symbol_buffer.getvalue()
            
            # Replace double-line borders with single-line borders for STATISTICS and ISSUES
            symbol_output = symbol_output.replace('╔', '')
            symbol_output = symbol_output.replace('╗', '')
            symbol_output = symbol_output.replace('╚', '')
            symbol_output = symbol_output.replace('╝', '')
            symbol_output = symbol_output.replace('╠', '')
            symbol_output = symbol_output.replace('╣', '')
            symbol_output = symbol_output.replace('║', '')
            symbol_output = symbol_output.replace('═', '')
            
            lines = symbol_output.split('\n')
            
            # Find where user-defined symbols section starts and skip all before it
            start_idx = None
            for i, line in enumerate(lines):
                if 'USER-DEFINED SYMBOLS' in line:
                    # Skip this header and continue 3 lines (for the box)
                    start_idx = i + 3
                    break
            
            # If no user-defined symbols section found, show everything
            if start_idx is None:
                print(symbol_output)
            else:
                # Print only from user-defined symbols onwards
                print('\n'.join(lines[start_idx:]))
            
            # Print Errors/Issues (if any)
            if error_handler.has_errors() or error_handler.has_warnings():
                print("\nErrors/Issues:")
                for err in error_handler.get_errors():
                    print(f"  {err}")
                
        except SyntaxError as e:
            print(f"\nSyntax Error: {e}")
        except Exception as e:
            print(f"\nSemantic analysis failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Re-enable logging after semantic analysis
            log.disable(log.NOTSET)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
