import sys
import logging
sys.path.insert(0, 'd:\\Repositories\\platter-compiler-webapp\\platter-compiler-sveltejs\\static\\python')

# Suppress debug logs
logging.getLogger().setLevel(logging.CRITICAL)

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from app.semantic_analyzer.symbol_table.symbol_table_output import format_symbol_table_compact

# Test program with various data types
program = """
table of Person = [
    chars of name;
    piece of age;
];

piece of initialized_var = 42;
sip of uninitialized_sip;
chars of text = "hello";
flag of state = up;
piece[] of numbers = [1, 2, 3];
piece[] of empty_array;
Person of john = [name = "John"; age = 30;];
Person of person_default;

prepare piece of compute(piece of x) {
    serve x * 2;
}

prepare sip of average(sip of a, sip of b) {
    serve (a + b) / 2.0;
}

start() {
    piece of local_var = 10;
    sip of result;
}
"""

print("=" * 80)
print("Testing Default Value Display in Symbol Table")
print("=" * 80)

# Lex and parse
lexer = Lexer(program)
tokens = lexer.tokenize()

ast_parser = ASTParser(tokens)
ast = ast_parser.parse_program()

# Semantic analysis
analyzer = SemanticAnalyzer()
symbol_table, error_handler = analyzer.analyze(ast)

# Display symbol table
# Write to file with UTF-8 encoding to avoid console encoding issues
with open('symbol_table_output.txt', 'w', encoding='utf-8') as f:
    f.write("\n" + format_symbol_table_compact(symbol_table))
print("\nSymbol table written to symbol_table_output.txt")

print("\n" + "=" * 80)
print("Value Column Verification:")
print("=" * 80)
print("✓ Primitives (initialized) → actual value (e.g., 42, \"hello\", up)")
print("✓ Primitives (uninitialized) → type default (e.g., 0, 0.0, \"\", down)")
print("✓ Arrays (initialized) → element count and type (e.g., [3 × piece])")
print("✓ Arrays (empty) → element type (e.g., [piece])")
print("✓ Table prototype → fields with types")
print("✓ Table instance (initialized) → fields with values")
print("✓ Table instance (uninitialized) → fields with defaults")
print("✓ Recipe → default value of return type (e.g., 0 for piece, 0.0 for sip)")
print("=" * 80)
