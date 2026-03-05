import sys
import logging
sys.path.insert(0, 'd:\\Repositories\\platter-compiler-webapp\\platter-compiler-sveltejs\\static\\python')

# Suppress debug logs
logging.getLogger().setLevel(logging.CRITICAL)

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from app.semantic_analyzer.symbol_table.symbol_table_output import format_symbol_table_compact

# Simple test program
program = """
table of Person = [
    chars of name;
    piece of age;
];

Person of person_default;
"""

# Lex and parse
lexer = Lexer(program)
tokens = lexer.tokenize()

parser = ASTParser(tokens)
ast = parser.parse_program()

# Semantic analysis
analyzer = SemanticAnalyzer()
symbol_table, _ = analyzer.analyze(ast)

# Check the person_default symbol
person_default = symbol_table.lookup_symbol("person_default")
print(f"Symbol: {person_default.name}")
print(f"Type base: {person_default.type_info.base_type}")
print(f"Type is_table: {person_default.type_info.is_table}")
print(f"Type dimensions: {person_default.type_info.dimensions}")
print(f"Type table_fields: {person_default.type_info.table_fields}")
print(f"Symbol value: {repr(person_default.value)}")

# Get Person table type
person_type = symbol_table.table_types.get("Person")
if person_type:
    print(f"\nPerson type_info:")
    print(f"  base_type: {person_type.base_type}")
    print(f"  is_table: {person_type.is_table}")
    print(f"  table_fields: {person_type.table_fields}")
