"""Test to check table prototype display issue"""

# Add to path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import analyze_program
from app.semantic_analyzer.symbol_table.symbol_table_output import format_symbol_table_compact

code = """
table of Data = [
    piece of x;
    chars of y;
    sip of z;
    flag of f;
];

prepare Data of getData() {
    Data of x;
    x:x = 1;
    x:y = "Raphael";
    x:z = 1.1;
    x:f = up;
    
    serve x;
}

start() {}
"""

# Lex and parse
lexer = Lexer(code)
tokens = lexer.tokenize()

# Check for lexer errors
if lexer.errors:
    print("Lexer errors:")
    for error in lexer.errors:
        print(f"  {error}")
    sys.exit(1)

# Generate AST directly
ast_parser = ASTParser(tokens)
ast = ast_parser.parse_program()

# Semantic analysis
symbol_table, error_handler = analyze_program(ast)

# Check Data symbol
data_symbol = symbol_table.lookup_symbol("Data")
print(f"Data symbol found: {data_symbol is not None}")
if data_symbol:
    print(f"  Kind: {data_symbol.kind}")
    print(f"  Kind value: {data_symbol.kind.value}")
    print(f"  Type: {data_symbol.type_info}")
    print(f"  Type base: {data_symbol.type_info.base_type}")
    print(f"  Is table: {data_symbol.type_info.is_table}")
    print(f"  Table fields: {list(data_symbol.type_info.table_fields.keys()) if data_symbol.type_info.table_fields else None}")

# Check getData symbol
get_data_symbol = symbol_table.lookup_symbol("getData")
print(f"\ngetData symbol found: {get_data_symbol is not None}")
if get_data_symbol:
    print(f"  Kind: {get_data_symbol.kind}")
    print(f"  Kind value: {get_data_symbol.kind.value}")
    print(f"  Type: {get_data_symbol.type_info}")
    print(f"  Type base: {get_data_symbol.type_info.base_type}")
    print(f"  Is table: {get_data_symbol.type_info.is_table}")

# Print formatted symbol table
print("\n" + "="*80)
print("FORMATTED SYMBOL TABLE:")
print("="*80)
print(format_symbol_table_compact(symbol_table, error_handler))
