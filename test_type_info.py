import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'platter-compiler-sveltejs' / 'static' / 'python'))

from app.semantic_analyzer.symbol_table.types import TypeInfo

# Test get_element_type
type_2d = TypeInfo("piece", 2)
print(f"Original type: {type_2d} (dimensions={type_2d.dimensions})")

type_1d = type_2d.get_element_type()
print(f"Element type: {type_1d} (dimensions={type_1d.dimensions})")

# Expected: piece[] (dimensions=1)
assert type_1d.dimensions == 1, f"Expected dimensions=1, got {type_1d.dimensions}"
print("✓ get_element_type() works correctly")
