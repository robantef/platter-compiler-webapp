"""
Comprehensive test showing all default value features
"""

from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

test_program = """
piece of a;
sip of b;
chars of c;
flag of d;

piece[] of arr1;
piece[][] of arr2;
chars[] of strs;

table of Person = [
    chars of name;
    piece of age;
];

Person of p1;
Person of p2 = [ name = "Alice"; age = 25; ];

prepare piece of sum(piece of x, piece of y) {
    serve x + y;
}

start() {
    piece of result = sum(a, 5);
}
"""

print("=" * 80)
print("DEFAULT VALUES AND STRICT TYPE CHECKING DEMONSTRATION")
print("=" * 80)

# Parse and analyze
lexer = Lexer(test_program)
tokens = lexer.tokenize()
parser = Parser(tokens)
parser.parse_program()
ast_parser = ASTParser(tokens)
ast = ast_parser.parse_program()
analyzer = SemanticAnalyzer()
symbol_table, error_handler = analyzer.analyze(ast)

# Generate symbol table output
from app.semantic_analyzer.symbol_table.symbol_table_output import format_symbol_table_compact
output = format_symbol_table_compact(symbol_table, error_handler)

with open("comprehensive_defaults.txt", "w", encoding="utf-8") as f:
    f.write(output)

print("\n✓ Symbol table output written to: comprehensive_defaults.txt")

if error_handler.has_errors():
    print("\n✗ Errors found:")
    print(error_handler.format_errors(include_warnings=False, include_info=False))
else:
    print("\n✓ No semantic errors")

print("\nDefault Values Summary:")
print("  - piece: 0")
print("  - sip: 0.0")
print("  - chars: \"\"")
print("  - flag: False (down)")
print("  - arrays: [] (nested properly for multi-dimensional)")
print("  - tables: all fields initialized with their default values")

print("\nStrict Type Checking:")
print("  - No implicit promotion between piece and sip")
print("  - Assignment requires exact type match")
print("  - Only exception: piece and sip compatible in operations (not assignments)")
