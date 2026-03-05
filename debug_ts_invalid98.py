import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'platter-compiler-sveltejs' / 'static' / 'python'))

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from app.semantic_analyzer.ast.ast_nodes import ArrayDecl, ArrayLiteral
from app.parser.parser_program import Parser

# Read the file
file_path = Path('platter-compiler-sveltejs/static/python/tests/semantic_programs/source_code/ts_invalid98.platter')
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

print("=== SOURCE CODE ===")
print(code)
print()

# Lexical analysis
lexer = Lexer(code)
tokens = lexer.tokenize()

# Syntax analysis
parser = Parser(tokens)
parser.parse_program()

# AST parsing
ast_parser = ASTParser(tokens)
ast = ast_parser.parse_program()

print("=== AST GLOBAL DECLARATIONS ===")
for decl in ast.global_decl:
    print(f"{decl.__class__.__name__}: {decl}")
print()

# Semantic analysis
analyzer = SemanticAnalyzer()
symbol_table, error_handler = analyzer.analyze(ast)

print("=== ARRAY DECLARATION DEBUG ===")
# Find the ArrayDecl node in start_platter
if ast.start_platter and ast.start_platter.local_decls:
    for decl in ast.start_platter.local_decls:
        if isinstance(decl, ArrayDecl):
            print(f"ArrayDecl: {decl}")
            print(f"  data_type: {decl.data_type}")
            print(f"  dimensions: {decl.dimensions}")
            print(f"  identifier: {decl.identifier}")
            print(f"  init_value type: {type(decl.init_value).__name__}")
            if isinstance(decl.init_value, ArrayLiteral):
                print(f"  init_value elements: {len(decl.init_value.elements)}")
                for i, elem in enumerate(decl.init_value.elements):
                    print(f"    Element {i}: {type(elem).__name__}")
print()

print("=== TABLE TYPES IN SYMBOL TABLE ===")
print(f"Table types: {list(symbol_table.table_types.keys())}")
if 'Student' in symbol_table.table_types:
    student_type = symbol_table.table_types['Student']
    print(f"Student type: {student_type}")
    print(f"Student fields: {student_type.table_fields}")
else:
    print("Student type NOT FOUND")
print()

print("=== SEMANTIC ERRORS ===")
if error_handler.has_errors() or error_handler.has_warnings():
    output = error_handler.format_errors(include_warnings=True, include_info=False)
    print(output)
    
    # Check if we got the expected error
    if "age" in output.lower() and "mismatch" in output.lower():
        print("\n[OK] Got expected field type mismatch error!")
    else:
        print("\n[MISS] Missing expected 'type mismatch on age field' error")
else:
    print("No semantic errors")
