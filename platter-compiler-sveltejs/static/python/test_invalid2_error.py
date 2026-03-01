"""
Test script to check error message for test_invalid2.platter
"""

from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

# Test program
test_program = """piece of x;
sip of y = x;
start() {}"""

print("Testing: test_invalid2.platter")
print("-" * 60)

# Lexical and syntax analysis
lexer = Lexer(test_program)
tokens = lexer.tokenize()

try:
    parser = Parser(tokens)
    parser.parse_program()
except Exception as e:
    print(f"Syntax error: {e}")
    exit(1)

# Semantic analysis
ast_parser = ASTParser(tokens)
ast = ast_parser.parse_program()
analyzer = SemanticAnalyzer()
symbol_table, error_handler = analyzer.analyze(ast)

# Output errors
if error_handler.has_errors() or error_handler.has_warnings():
    output = error_handler.format_errors(include_warnings=True, include_info=False)
    print("\nError output:")
    print(output)
else:
    print("\nNo semantic errors")

# Also test default values
print("\n" + "=" * 60)
print("Testing default values:")
print("=" * 60)

test_defaults = """piece of a;
sip of b;
chars of c;
flag of d;
piece[] of e;
piece[][] of f;

table of Person = [
    chars of name;
    piece of age;
];

Person of p1;

start() {}"""

lexer2 = Lexer(test_defaults)
tokens2 = lexer2.tokenize()
parser2 = Parser(tokens2)
parser2.parse_program()
ast_parser2 = ASTParser(tokens2)
ast2 = ast_parser2.parse_program()
analyzer2 = SemanticAnalyzer()
symbol_table2, error_handler2 = analyzer2.analyze(ast2)

from app.semantic_analyzer.symbol_table.symbol_table_output import format_symbol_table_compact
with open("default_values_test.txt", "w", encoding="utf-8") as f:
    f.write(format_symbol_table_compact(symbol_table2, error_handler2))

print("\nSymbol table with default values written to: default_values_test.txt")
