import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from semantic_analyzer.symbol_table.types import Symbol, TypeInfo, SymbolKind
from semantic_analyzer.ast.ast_nodes import Literal
from lexer.token import Token

# Create a simple piece variable with value 42
type_info = TypeInfo(base_type="piece", dimensions=0)

# Create a Literal node with integer value 42
literal_node = Literal(value_type="piece", value=42, line=1, column=1)

# Create a mock declaration node
class MockDecl:
    def __init__(self):
        self.init_value = literal_node
        self.line = 1
        self.column = 1

decl_node = MockDecl()

# Create symbol
symbol = Symbol(
    name="test_var",
    kind=SymbolKind.VARIABLE,
    type_info=type_info,
    declaration_node=decl_node,
    scope_level=0
)

# Compute default value
print(f"Before compute - Symbol value: {repr(symbol.value)}")
print(f"Declaration node has init_value: {hasattr(decl_node, 'init_value')}")
print(f"Init value is: {decl_node.init_value}")
print(f"Init value type: {type(decl_node.init_value)}")

symbol.compute_default_value()

print(f"\nAfter compute - Symbol value: {repr(symbol.value)}")
print(f"Symbol value type: {type(symbol.value)}")
print(f"Literal node value: {repr(literal_node.value)}")
print(f"Literal node value type: {type(literal_node.value)}")
