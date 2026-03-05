import sys
sys.path.insert(0, 'd:\\Repositories\\platter-compiler-webapp\\platter-compiler-sveltejs\\static\\python\\app')

from semantic_analyzer.symbol_table.types import Symbol, TypeInfo, SymbolKind

# Create a TypeInfo for chars
chars_type = TypeInfo(base_type="chars", dimensions=0)

# Create a dummy symbol to test _get_type_default
symbol = Symbol("test", SymbolKind.VARIABLE, chars_type, 0)

# Test _get_type_default
result = symbol._get_type_default(chars_type, {})
print(f"Default for chars type: {repr(result)}")
print(f"Length: {len(result)}")
print(f"Characters: {[ord(c) for c in result]}")

# Now test table instance with chars field
table_fields = {
    "name": TypeInfo("chars", 0),
    "age": TypeInfo("piece", 0)
}
table_type = TypeInfo(base_type="Person", dimensions=0, table_fields=table_fields)
table_type.is_table = True

result2 = symbol._get_type_default(table_type, {})
print(f"\nDefault for Person table: {repr(result2)}")
print(f"Actual output: {result2}")
