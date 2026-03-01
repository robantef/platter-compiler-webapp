"""
Built-in Recipes (Functions) for Platter Language
Defines type signatures and spice (parameter) specifications for all built-in recipes
"""

from app.semantic_analyzer.symbol_table.types import TypeInfo
from typing import List, Tuple


class BuiltinRecipeSignature:
    """Represents a built-in recipe's type signature"""
    
    def __init__(self, name: str, return_type: str, return_dims: int, 
                 spices: List[Tuple[str, int]], description: str = ""):
        """
        Initialize a built-in recipe signature
        
        Args:
            name: Recipe name
            return_type: Return type (piece, sip, chars, flag, void)
            return_dims: Number of array dimensions for return type
            spices: List of (type, dimensions) tuples for each spice (parameter)
            description: Description of what the recipe does
        """
        self.name = name
        self.return_type = return_type
        self.return_dims = return_dims
        self.spices = spices  # List of (type_name, dimensions) tuples
        self.description = description
    
    def get_return_type_info(self) -> TypeInfo:
        """Get TypeInfo for the return type"""
        return TypeInfo(self.return_type, self.return_dims)
    
    def get_spice_type_info(self, index: int) -> TypeInfo:
        """Get TypeInfo for a specific spice (parameter)"""
        if 0 <= index < len(self.spices):
            type_name, dims = self.spices[index]
            return TypeInfo(type_name, dims)
        return None
    
    def get_spice_count(self) -> int:
        """Get the number of spices (parameters)"""
        return len(self.spices)
    
    def __repr__(self):
        return f"BuiltinRecipe({self.name}: {self.return_type}, {len(self.spices)} spices)"


# Built-in recipe definitions
# Format: name -> [list of signatures] to support overloading
# All overloads have the same arity and return type, but different parameter types
BUILTIN_RECIPES = {
    # Type conversion recipes (with overloads for different input types)
    "topiece": [
        BuiltinRecipeSignature(
            "topiece", "piece", 0, 
            [("piece", 0)],
            "Convert piece to piece (does nothing)"
        ),
        BuiltinRecipeSignature(
            "topiece", "piece", 0, 
            [("chars", 0)],
            "Convert chars to piece (integer)"
        ),
        BuiltinRecipeSignature(
            "topiece", "piece", 0, 
            [("sip", 0)],
            "Convert sip to piece (integer)"
        ),
        BuiltinRecipeSignature(
            "topiece", "piece", 0, 
            [("flag", 0)],
            "Convert flag to piece (integer)"
        ),
    ],
    
    "tosip": [
        BuiltinRecipeSignature(
            "tosip", "sip", 0,
            [("sip", 0)],
            "Convert sip to sip (does nothing)"
        ),
        BuiltinRecipeSignature(
            "tosip", "sip", 0,
            [("piece", 0)],
            "Convert piece to sip (float)"
        ),
        BuiltinRecipeSignature(
            "tosip", "sip", 0,
            [("chars", 0)],
            "Convert chars to sip (float)"
        ),
        BuiltinRecipeSignature(
            "tosip", "sip", 0,
            [("flag", 0)],
            "Convert flag to sip (float)"
        ),
    ],
    
    "tochars": [
        BuiltinRecipeSignature(
            "tochars", "chars", 0,
            [("chars", 0)],
            "Convert chars to chars (does nothing)"
        ),
        BuiltinRecipeSignature(
            "tochars", "chars", 0,
            [("piece", 0)],
            "Convert piece to chars (string)"
        ),
        BuiltinRecipeSignature(
            "tochars", "chars", 0,
            [("sip", 0)],
            "Convert sip to chars (string)"
        ),
        BuiltinRecipeSignature(
            "tochars", "chars", 0,
            [("flag", 0)],
            "Convert flag to chars (string)"
        ),
    ],

    # Input and Output recipes
    "take": [
        BuiltinRecipeSignature(
            "take", "chars", 0,
            [],
            "Read input no params"
        ),
    ],
    
    "bill": [
        BuiltinRecipeSignature(
            "bill", "chars", 0,
            [("chars", 0)],
            "Print chars to output"
        ),
    ],
    
     # Math and Formatting recipes   
    "pow": [
        BuiltinRecipeSignature(
            "pow", "piece", 0,
            [("piece", 0), ("piece", 0)],
            "Calculate power (piece^piece)"
        ),
    ],

    "sqrt": [
        BuiltinRecipeSignature(
            "sqrt", "sip", 0,
            [("piece", 0)],
            "Calculate square root of piece -> sip"
        ),
    ],
    
    "fact": [
        BuiltinRecipeSignature(
            "fact", "piece", 0,
            [("piece", 0)],
            "Calculate factorial (piece only)"
        ),
    ],
    
    "cut": [
        BuiltinRecipeSignature(
            "cut", "chars", 0,
            [("sip", 0), ("sip", 0)],
            "Format sip to chars cut(x,y) where <x>.<y> result digits"
        ),
    ],
    
    "copy": [
        BuiltinRecipeSignature(
            "copy", "chars", 0,
            [("chars", 0), ("piece", 0), ("piece", 0)],
            "Extracts a substring based on character position copy(chars,start,end)"
        ),
    ],

    "rand": [
        BuiltinRecipeSignature(
            "rand", "sip", 0,
            [],
            "Generate random sip integer between 0 and 1, exclusive"
        ),
    ],
    
    # Array and Table recipes
    "size": [
        BuiltinRecipeSignature(
            "size", "piece", 0,
            [("piece", 1)],
            "Get the size (length) of piece array"
        ),
        BuiltinRecipeSignature(
            "size", "piece", 0,
            [("sip", 1)],
            "Get the size (length) of sip array"
        ),
        BuiltinRecipeSignature(
            "size", "piece", 0,
            [("chars", 1)],
            "Get the size (length) of chars array"
        ),
        BuiltinRecipeSignature(
            "size", "piece", 0,
            [("flag", 1)],
            "Get the size (length) of flag array"
        ),
    ],
    
    "sort": [
        BuiltinRecipeSignature(
            "sort", "piece", 1,
            [("piece", 1)],
            "Sort piece array in place"
        ),
        BuiltinRecipeSignature(
            "sort", "sip", 1,
            [("sip", 1)],
            "Sort sip array in place"
        ),
        BuiltinRecipeSignature(
            "sort", "chars", 1,
            [("chars", 1)],
            "Sort chars array in place"
        ),
    ],
    
    "search": [
        BuiltinRecipeSignature(
            "search", "piece", 0,
            [("piece", 1), ("piece", 0)],
            "Search for piece element, return index or -1"
        ),
        BuiltinRecipeSignature(
            "search", "piece", 0,
            [("sip", 1), ("sip", 0)],
            "Search for sip element, return index or -1"
        ),
        BuiltinRecipeSignature(
            "search", "piece", 0,
            [("chars",1), ("chars", 0)],
            "Search for chars element, return index or -1"
        ),
    ],
    
    "reverse": [
        BuiltinRecipeSignature(
            "reverse", "piece", 1,
            [("piece", 1)],
            "Reverse piece array in place"
        ),
        BuiltinRecipeSignature(
            "reverse", "sip", 1,
            [("sip", 1)],
            "Reverse sip array in place"
        ),
        BuiltinRecipeSignature(
            "reverse", "chars", 1,
            [("chars", 1)],
            "Reverse chars array in place"
        ),
        BuiltinRecipeSignature(
            "reverse", "flag", 1,
            [("flag", 1)],
            "Reverse flag array in place"
        ),
    ],
    
    "append": [
        BuiltinRecipeSignature(
            "append", "piece", 1,
            [("piece", 1), ("piece", 0)],
            "Append piece element to piece array"
        ),
        BuiltinRecipeSignature(
            "append", "sip", 1,
            [("sip", 1), ("sip", 0)],
            "Append sip element to sip array"
        ),
        BuiltinRecipeSignature(
            "append", "chars", 1,
            [("chars", 1), ("chars", 0)],
            "Append chars element to chars array"
        ),
        BuiltinRecipeSignature(
            "append", "flag", 1,
            [("flag", 1), ("flag", 0)],
            "Append flag element to flag array"
        ),
    ],
    
    "remove": [
        BuiltinRecipeSignature(
            "remove", "piece", 1,
            [("piece", 1), ("piece", 0)],
            "Remove piece at index from piece array element and return new array"
        ),
        BuiltinRecipeSignature(
            "remove", "sip", 1,
            [("sip", 1), ("piece", 0)],
            "Remove sip at index from piece array element and return new array"
        ),
        BuiltinRecipeSignature(
            "remove", "chars", 1,
            [("chars", 1), ("piece", 0)],
            "Remove chars at index from piece array element and return new array"
        ),
        BuiltinRecipeSignature(
            "remove", "flag", 1,
            [("flag", 1), ("piece", 0)],
            "Remove flag at index from piece array element and return new array"
        ),
    ],
    
    "matches": [
        # Arrays
        BuiltinRecipeSignature(
            "matches", "flag", 0,
            [("piece", 1), ("piece", 1)],
            "Check if two piece arrays have the same elements"
        ),
        BuiltinRecipeSignature(
            "matches", "flag", 0,
            [("sip", 1), ("sip", 1)],
            "Check if two sip arrays have the same elements"
        ),
        BuiltinRecipeSignature(
            "matches", "flag", 0,
            [("chars", 1), ("chars", 1)],
            "Check if two chars arrays have the same elements"
        ),
        BuiltinRecipeSignature(
            "matches", "flag", 0,
            [("flag", 1), ("flag", 1)],
            "Check if two flag arrays have the same elements"
        ),
        # Tables/Structs (assuming type name is 'table' or 'struct')
        BuiltinRecipeSignature(
            "matches", "flag", 0,
            [("table", 0), ("table", 0)],
            "Check if two tables have the same fields and values"
        ),
        # Table/Struct arrays
        BuiltinRecipeSignature(
            "matches", "flag", 0,
            [("table", 1), ("table", 1)],
            "Check if two table arrays have the same elements"
        ),
    ],
}


def get_builtin_recipe(name: str) -> List[BuiltinRecipeSignature]:
    """
    Get all built-in recipe signature overloads by name
    
    Args:
        name: Recipe name
    
    Returns:
        List of BuiltinRecipeSignature overloads if found, empty list otherwise
    """
    return BUILTIN_RECIPES.get(name, [])


def get_builtin_recipe_overload(name: str, arg_types: List[Tuple[str, int]]) -> BuiltinRecipeSignature:
    """
    Get a specific built-in recipe overload by name and argument types
    
    Args:
        name: Recipe name
        arg_types: List of (type_name, dimensions) tuples for arguments
    
    Returns:
        Matching BuiltinRecipeSignature if found, None otherwise
    """
    overloads = BUILTIN_RECIPES.get(name, [])
    for overload in overloads:
        if overload.spices == arg_types:
            return overload
    return None


def find_compatible_builtin_overload(name: str, arg_types: List[Tuple[str, int]]) -> BuiltinRecipeSignature:
    """
    Find a compatible built-in recipe overload by name and argument types.
    Allows some type flexibility (e.g., piece and sip are compatible).
    
    Args:
        name: Recipe name
        arg_types: List of (type_name, dimensions) tuples for arguments
    
    Returns:
        Compatible BuiltinRecipeSignature if found, None otherwise
    """
    overloads = BUILTIN_RECIPES.get(name, [])
    
    # First try exact match
    for overload in overloads:
        if overload.spices == arg_types:
            return overload
    
    # Then try compatible match (piece <-> sip)
    for overload in overloads:
        if len(overload.spices) != len(arg_types):
            continue
        
        compatible = True
        for i, (expected_type, expected_dims) in enumerate(overload.spices):
            actual_type, actual_dims = arg_types[i]
            
            # Dimensions must match exactly
            if expected_dims != actual_dims:
                compatible = False
                break
            
            # Types must match or be compatible (piece <-> sip)
            if expected_type != actual_type:
                if not ({expected_type, actual_type} == {"piece", "sip"}):
                    compatible = False
                    break
        
        if compatible:
            return overload
    
    return None


def is_builtin_recipe(name: str) -> bool:
    """
    Check if a name is a built-in recipe
    
    Args:
        name: Recipe name to check
    
    Returns:
        True if it's a built-in recipe, False otherwise
    """
    return name in BUILTIN_RECIPES


def get_all_builtin_recipe_names() -> List[str]:
    """Get list of all built-in recipe names"""
    return list(BUILTIN_RECIPES.keys())
