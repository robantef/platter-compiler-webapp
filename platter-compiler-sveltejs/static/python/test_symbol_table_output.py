"""
Test script to see enhanced symbol table output
"""

from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

# Test program with table prototype and table instance
test_program = """table of Class = [ chars of blk_name; ]; 
Class of blk1 = [ blk_name = "Mahusay"; ];

start() { blk1:blk_name = "2";}"""

print("=" * 80)
print("Testing Enhanced Symbol Table Output")
print("=" * 80)
print("\nSource Code:")
print(test_program)
print("\n" + "=" * 80)

# Lexical analysis
lexer = Lexer(test_program)
tokens = lexer.tokenize()

# Syntax analysis
try:
    parser = Parser(tokens)
    parser.parse_program()
    print("\n[OK] Syntax analysis passed!")
except Exception as e:
    print(f"\n[ERROR] Syntax error: {e}")
    exit(1)

# Semantic analysis with AST
ast_parser = ASTParser(tokens)
ast = ast_parser.parse_program()

print("\nRunning Semantic Analysis...")
analyzer = SemanticAnalyzer()
symbol_table, error_handler = analyzer.analyze(ast)

print("\n" + "=" * 80)
print("Symbol Table Output:")
print("=" * 80)

# Debug: Check if Class symbol has table_fields
class_symbol = symbol_table.lookup_symbol('Class')
if class_symbol:
    print(f"\nDEBUG - Class symbol:")
    print(f"  - kind: {class_symbol.kind}")
    print(f"  - type_info.is_table: {class_symbol.type_info.is_table}")
    print(f"  - type_info.table_fields: {class_symbol.type_info.table_fields}")
    print(f"  - declaration_node: {class_symbol.declaration_node}")
    print()

from app.semantic_analyzer.symbol_table.symbol_table_output import format_symbol_table_compact
output = format_symbol_table_compact(symbol_table, error_handler)

# Write to file to avoid Unicode encoding issues
with open("symbol_table_output.txt", "w", encoding="utf-8") as f:
    f.write(output)

print("\n[OK] Symbol table output written to: symbol_table_output.txt")
print("\nSummary:")
print("  - Table Prototype 'Class': Shows as 'table<Class>' with field structure")
print("  - Table Instance 'blk1': Shows as '->Class' with initialization values")
print("  - Field values are displayed verbosely with types and contents")
