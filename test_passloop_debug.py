"""
Debug test to inspect AST structure for PassLoop
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'platter-compiler-sveltejs', 'static', 'python')))

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.ast.ast_nodes import *

# Test case
source_code = """
start() {
    pass (i = 0; i += 1; (i > 4)) {
    }
}
"""

print("Parsing source code...")
lexer = Lexer(source_code)
tokens = lexer.tokenize()
parser = ASTParser(tokens)
ast = parser.parse_program()

print("\n=== AST STRUCTURE ===\n")

# Check start_platter
if ast.start_platter:
    print("✓ start_platter exists")
    platter = ast.start_platter
    print(f"  - local_decls: {len(platter.local_decls)}")
    print(f"  - statements: {len(platter.statements)}")
    
    for i, stmt in enumerate(platter.statements):
        print(f"\n  Statement {i}: {type(stmt).__name__}")
        
        if isinstance(stmt, PassLoop):
            print("  ✓ Found PassLoop!")
            print(f"    - init: {type(stmt.init).__name__ if stmt.init else 'None'}")
            if isinstance(stmt.init, Assignment):
                print(f"      - target: {type(stmt.init.target).__name__}")
                if isinstance(stmt.init.target, Identifier):
                    print(f"        - name: '{stmt.init.target.name}'")
                print(f"      - operator: '{stmt.init.operator}'")
                print(f"      - value: {type(stmt.init.value).__name__}")
            
            print(f"    - condition: {type(stmt.condition).__name__ if stmt.condition else 'None'}")
            print(f"    - update: {type(stmt.update).__name__ if stmt.update else 'None'}")
            if isinstance(stmt.update, Assignment):
                print(f"      - target: {type(stmt.update.target).__name__}")
                if isinstance(stmt.update.target, Identifier):
                    print(f"        - name: '{stmt.update.target.name}'")
                print(f"      - operator: '{stmt.update.operator}'")
            print(f"    - body: {type(stmt.body).__name__}")
else:
    print("✗ No start_platter found!")

print("\n=== RUNNING SEMANTIC ANALYZER ===\n")

from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

try:
    analyzer = SemanticAnalyzer()
    symbol_table, error_handler = analyzer.analyze(ast)
    print("✓ Semantic analyzer completed successfully")
except Exception as e:
    print(f"✗ Exception during semantic analysis: {e}")
    import traceback
    traceback.print_exc()
    import sys
    sys.exit(1)

print(f"Errors: {error_handler.get_error_count()}")
print(f"Warnings: {error_handler.get_warning_count()}")

if error_handler.has_errors():
    print("\nERRORS:")
    for error in error_handler.errors:
        print(f"  - {error['message']} (code: {error['code']})")
else:
    print("\n✗ NO ERRORS - This is unexpected!")

if error_handler.warnings:
    print("\nWARNINGS:")
    for warning in error_handler.warnings:
        print(f"  - {warning['message']}")

print("\n" + "="*60)
print(f"Expected: 3 errors about undefined 'i'")
print(f"Actual: {error_handler.get_error_count()} error(s) found")
