import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.symbol_table.symbol_table_builder import SymbolTableBuilder
from app.semantic_analyzer.semantic_passes.error_handler import SemanticErrorHandler
from app.semantic_analyzer.semantic_passes.scope_checker import ScopeChecker

source_code = """
prepare piece[] of mergeSort(piece[] of arr) {
    piece of n;
    piece of mid;
    piece of i;
    piece[] of left;
    piece[] of right;
    piece[] of sortedLeft;
    piece[] of sortedRight;
    piece[] of result;

    n = size(arr);

    check(n <= (1)) {
        serve [arr];
    }

    mid = n / (2);
    left = [];
    right = [];

    # copy left half
    pass(i=0; i+=1; i<mid) {
        append(left, arr[i]);
    }

    # copy right half
    pass(i=mid; i+=1; i<n) {
        append(right, arr[i]);
    }

    sortedLeft = mergeSort(left);
    sortedRight = mergeSort(right);

    result = merge(sortedLeft, sortedRight);
    serve [result];
}

prepare piece[] of merge(piece[] of left, piece[] of right) {
    piece of i,j,k;
    piece[] of merged;

    i = (0);
    j = (0);
    merged = [];

    pass(k=0; k+=1; k<size(left)+size(right)) {
        check(i < size(left) and (j >= size(right) or left[i] <= right[j])) {
            append(merged, left[i]);
            i += (1);
        }
        alt(j < size(right)) {
            append(merged, right[j]);
            j += (1);
        }
    }
    serve [merged];
}

start() {
    piece[] of arr;
    piece[] of sorted;

    arr = [38,27,43,3,9,82,10];
    sorted = mergeSort(arr);
    serve [sorted];
}
"""

lexer = Lexer(source_code)
tokens = lexer.tokenize()
parser = ASTParser(tokens)
ast = parser.parse_program()

error_handler = SemanticErrorHandler()

# 1. Build Scope
builder = SymbolTableBuilder()
builder.symbol_table.error_handler = error_handler
symbol_table = builder.build(ast)

# 2. Scope Checker
checker = ScopeChecker(symbol_table, error_handler)
checker.check(ast)

# 3. Type Checker
from app.semantic_analyzer.semantic_passes.type_checker import TypeChecker
type_checker = TypeChecker(symbol_table, error_handler)
type_checker.check(ast)

print("Statements inside Platter:")
from app.semantic_analyzer.ast.ast_nodes import PassLoop, RepeatLoop, Assignment, BinaryOp

for recipe in getattr(ast, 'recipe_decl', []):
    print("Recipe:", recipe.name)
    print("  Return Type:", getattr(recipe, 'return_type', None))
    print("  Return Dims:", getattr(recipe, 'return_dims', None))

def print_expr(expr, indent=""):
    if isinstance(expr, BinaryOp):
        print(indent + f"BinaryOp({expr.operator})")
        print_expr(expr.left, indent + "  ")
        print_expr(expr.right, indent + "  ")
    else:
        print(indent + str(type(expr)) + " " + getattr(expr, 'name', ''))

def print_block(statements, indent="  "):
    for s in statements:
        if isinstance(s, Assignment):
            print(indent + "Assignment:")
            print(indent + "  target:", type(s.target), getattr(s.target, 'name', None), getattr(s.target, 'array', None))
            print(indent + "  value:", type(s.value), getattr(s.value, 'name', None))
        elif isinstance(s, RepeatLoop):
            print(indent + "RepeatLoop with", len(s.body.statements), "statements")
            print_block(s.body.statements, indent + "  ")
        elif isinstance(s, PassLoop):
            print(indent + "PassLoop condition:")
            print_expr(s.condition, indent + "  ")
        else:
            print(indent + str(type(s)))

print_block(ast.start_platter.statements)

print("\nGlobal Symbols:")
for key, symbol in symbol_table.global_scope.symbols.items():
    print(f"  {key} -> {symbol.type_info}")

print("\nUsed symbols:", checker.used_symbols)
print("\nErrors:", error_handler.get_errors())
