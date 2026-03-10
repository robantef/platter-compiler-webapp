import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ''))

from app.lexer.lexer import Lexer
from app.parser.parser_platter import Parser

# Read the test file
with open('tests/semantic_programs/source_code/ts_algo9.platter', 'r') as f:
    source_code = f.read()

# Lexer
lexer = Lexer(source_code)
tokens = lexer.tokenize()

# Parser
parser = Parser(tokens)
ast = parser.parse()

# Print assignments in mergeSort function
def dump_assignments(node, indent=0):
    from app.parser.ast_nodes import Assignment, RecipeDeclaration, Identifier, RecipeCall
    
    if isinstance(node, RecipeDeclaration):
        print(f"{' ' * indent}RecipeDeclaration: {node.name} at line {node.line}")
        for stmt in node.body:
            dump_assignments(stmt, indent + 2)
    elif isinstance(node, Assignment):
        target_name = node.target.name if isinstance(node.target, Identifier) else "?"
        value_name = node.value.name if isinstance(node.value, (Identifier, RecipeCall)) else type(node.value).__name__
        print(f"{' ' * indent}Assignment at line {node.line}: {target_name} = {value_name}")
        print(f"{' ' * indent}  target at line {node.target.line}, col {node.target.column}")
        print(f"{' ' * indent}  value at line {node.value.line}")
    elif hasattr(node, '__dict__'):
        for attr_name, attr_value in node.__dict__.items():
            if isinstance(attr_value, list):
                for item in attr_value:
                    dump_assignments(item, indent)
            elif hasattr(attr_value, '__dict__'):
                dump_assignments(attr_value, indent)

# Start with the program node
dump_assignments(ast)
