#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from app.lexer.lexer import Lexer  
from app.parser.parser_program import Parser
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer

with open('tests/semantic_programs/source_code/ts_algo9.platter', 'r') as f:
    code = f.read()

# Lex
lexer = Lexer(code)
tokens = lexer.tokenize()
tokens = [t for t in tokens if t.type not in ("comment", "space", "newline", "tab")]

# Parse AST
ast_parser = ASTParser(tokens)
ast = ast_parser.parse_program()

# Dump assignments and declarations in mergeSort
print("\n=== AST DUMP ===")
from app.semantic_analyzer.ast.ast_nodes import Assignment, RecipeDecl, Identifier, RecipeCall, IngrDecl, ArrayDecl

for decl in ast.recipe_decl:
    if isinstance(decl, RecipeDecl) and decl.name == "mergeSort":
        print(f"RecipeDecl: {decl.name} at line {decl.line}")
        print("Local declarations:")
        for local_decl in decl.body.local_decls:
            if isinstance(local_decl, (IngrDecl, ArrayDecl)):
                decl_type = type(local_decl).__name__
                name = local_decl.identifier if hasattr(local_decl, 'identifier') else '?'
                has_init = local_decl.init_value is not None
                print(f"  {decl_type} at line {local_decl.line}: {name}, has_init={has_init}")
                if has_init and isinstance(local_decl.init_value, RecipeCall):
                    print(f"    init is RecipeCall: {local_decl.init_value.name}")
        print("Statements:")
        for stmt in decl.body.statements:
            if isinstance(stmt, Assignment):
                target_name = stmt.target.name if isinstance(stmt.target, Identifier) else "?"
                value_name = stmt.value.name if isinstance(stmt.value, (Identifier, RecipeCall)) else type(stmt.value).__name__
                print(f"  Assignment at line {stmt.line}: {target_name} = {value_name}")
                print(f"    target '{target_name}' at line {stmt.target.line}, col {stmt.target.column}")
print("=== END AST DUMP ===\n")

# Semantic analysis
analyzer = SemanticAnalyzer()
symbol_table, error_handler = analyzer.analyze(ast)

# Check symbol table
print("Global symbols:")
for name, symbol in symbol_table.global_scope.symbols.items():
    print(f"  {name}: {symbol.kind} -> {symbol.type_info}")

print(f"\nErrors: {error_handler.get_error_count()}")
for err in error_handler.get_errors():
    print(f"  - {err}")
    
print(f"\nWarnings: {error_handler.get_warning_count()}")
for warn in error_handler.get_warnings():
    print(f"  - {warn}")
