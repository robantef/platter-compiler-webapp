"""
Comprehensive test showing all enhanced symbol table features:
- Table prototypes with field structure
- Table instances with verbose initialization
- Array elements with type information
- Identifier references with @ notation
"""

from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

# Complex test program
test_program = """table of Person = [ 
    chars of name; 
    piece of age; 
]; 

prepare Person of createPerson(chars of n, piece of a){
    Person of p = [ name = n; age = a; ];
    serve p;
}

start() { 
    piece of x = 42;
    piece[] of numbers = [1, 2, 3, 4, 5];
    chars[] of names = ["Alice", "Bob", "Charlie"];
    Person of john = createPerson("John", 30);
}"""

print("=" * 80)
print("COMPREHENSIVE SYMBOL TABLE OUTPUT TEST")
print("=" * 80)
print("\nSource Code:")
print(test_program)
print("\n" + "=" * 80)

# Lexical and syntax analysis
lexer = Lexer(test_program)
tokens = lexer.tokenize()

try:
    parser = Parser(tokens)
    parser.parse_program()
except Exception as e:
    print(f"[ERROR] Syntax error: {e}")
    exit(1)

# Semantic analysis
ast_parser = ASTParser(tokens)
ast = ast_parser.parse_program()
analyzer = SemanticAnalyzer()
symbol_table, error_handler = analyzer.analyze(ast)

# Generate and save output
from app.semantic_analyzer.symbol_table.symbol_table_output import format_symbol_table_compact
output = format_symbol_table_compact(symbol_table, error_handler)

with open("comprehensive_symbol_table.txt", "w", encoding="utf-8") as f:
    f.write(output)

print("\n[OK] Symbol table output written to: comprehensive_symbol_table.txt")
print("\nEnhanced Features Demonstrated:")
print("  1. Table Prototype 'Person': Type='table<Person>', Fields displayed")
print("  2. Table Instances: Type='→Person' with verbose initialization")
print("  3. Array Types: Show element count and type (e.g., '[5 × piece]')")
print("  4. String Values: Displayed with quotes")
print("  5. Numeric Values: Displayed directly")
print("  6. Identifier References: Show with @ notation (e.g., '@john')")
print("  7. Multi-field Tables: Shows first 2 fields + count if more than 2")
