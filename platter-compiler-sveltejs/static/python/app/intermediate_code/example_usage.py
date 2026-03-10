"""
Example usage of the Intermediate Code Generator

This file demonstrates how to use the IR generator to create
Three Address Code (TAC) and Quadruples from an AST.
"""

import sys
import os

# Add parent directories to path
app_dir = os.path.dirname(os.path.dirname(__file__))
python_dir = os.path.dirname(app_dir)
sys.path.insert(0, python_dir)
sys.path.insert(0, app_dir)

from app.semantic_analyzer.ast.ast_nodes import *
from app.intermediate_code import IRGenerator, format_ir, IRFormatter


def create_sample_ast():
    """Create a simple sample AST for testing"""
    
    # Create a program with a simple function
    prog = Program()
    
    # Global variable: piece x = 10
    x_decl = VarDecl("piece", "x", Literal("piece", 10))
    prog.add_global_decl(x_decl)
    
    # Recipe: piece add(piece a, piece b) { serve a + b; }
    params = [
        ParamDecl("piece", 0, "a"),
        ParamDecl("piece", 0, "b")
    ]
    
    # Create body: serve a + b;
    add_expr = BinaryOp(Identifier("a"), "+", Identifier("b"))
    return_stmt = ReturnStatement(add_expr)
    body = Platter([], [return_stmt])
    
    add_recipe = RecipeDecl("piece", 0, "add", params, body)
    prog.add_recipe_decl(add_recipe)
    
    # Main start() platter
    # {
    #     piece result = 0;
    #     result = add(5, 3);
    # }
    result_decl = VarDecl("piece", "result", Literal("piece", 0))
    
    call_expr = FunctionCall("add", [Literal("piece", 5), Literal("piece", 3)])
    assign_stmt = Assignment(Identifier("result"), "=", call_expr)
    
    start_platter = Platter([result_decl], [assign_stmt])
    prog.set_start_platter(start_platter)
    
    return prog


def create_loop_example():
    """Create an AST with loops and conditionals"""
    
    prog = Program()
    
    # Main start() platter
    # {
    #     piece i = 0;
    #     piece sum = 0;
    #     
    #     repeat (i < 10) {
    #         check (i % 2 == 0) {
    #             sum = sum + i;
    #         }
    #         i = i + 1;
    #     }
    # }
    
    # Declarations
    i_decl = VarDecl("piece", "i", Literal("piece", 0))
    sum_decl = VarDecl("piece", "sum", Literal("piece", 0))
    
    # Loop condition: i < 10
    loop_cond = BinaryOp(Identifier("i"), "<", Literal("piece", 10))
    
    # If condition: i % 2 == 0
    mod_expr = BinaryOp(Identifier("i"), "%", Literal("piece", 2))
    if_cond = BinaryOp(mod_expr, "==", Literal("piece", 0))
    
    # If body: sum = sum + i
    sum_add = BinaryOp(Identifier("sum"), "+", Identifier("i"))
    sum_assign = Assignment(Identifier("sum"), "=", sum_add)
    if_body = Platter([], [sum_assign])
    
    if_stmt = IfStatement(if_cond, if_body)
    
    # i = i + 1
    i_inc = BinaryOp(Identifier("i"), "+", Literal("piece", 1))
    i_assign = Assignment(Identifier("i"), "=", i_inc)
    
    # While loop body
    loop_body = Platter([], [if_stmt, i_assign])
    
    while_loop = WhileLoop(loop_cond, loop_body)
    
    start_platter = Platter([i_decl, sum_decl], [while_loop])
    prog.set_start_platter(start_platter)
    
    return prog


def create_array_example():
    """Create an AST with array operations"""
    
    prog = Program()
    
    # Main start() platter
    # {
    #     piece[] arr;
    #     piece i = 0;
    #     arr[0] = 10;
    #     arr[1] = 20;
    #     i = arr[0] + arr[1];
    # }
    
    # Array declaration
    arr_decl = ArrayDecl("piece", 1, "arr")
    i_decl = VarDecl("piece", "i", Literal("piece", 0))
    
    # arr[0] = 10
    arr_assign1 = Assignment(
        ArrayAccess(Identifier("arr"), Literal("piece", 0)),
        "=",
        Literal("piece", 10)
    )
    
    # arr[1] = 20
    arr_assign2 = Assignment(
        ArrayAccess(Identifier("arr"), Literal("piece", 1)),
        "=",
        Literal("piece", 20)
    )
    
    # i = arr[0] + arr[1]
    arr_access1 = ArrayAccess(Identifier("arr"), Literal("piece", 0))
    arr_access2 = ArrayAccess(Identifier("arr"), Literal("piece", 1))
    add_expr = BinaryOp(arr_access1, "+", arr_access2)
    i_assign = Assignment(Identifier("i"), "=", add_expr)
    
    start_platter = Platter([arr_decl, i_decl], [arr_assign1, arr_assign2, i_assign])
    prog.set_start_platter(start_platter)
    
    return prog


def main():
    """Main function to demonstrate IR generation"""
    
    print("=" * 70)
    print("PLATTER INTERMEDIATE CODE GENERATOR - EXAMPLES")
    print("=" * 70)
    print()
    
    # Example 1: Simple function call
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Simple Function Call")
    print("=" * 70)
    
    ast1 = create_sample_ast()
    generator1 = IRGenerator()
    tac1, quads1 = generator1.generate(ast1)
    
    print("\nGenerated IR:")
    print(format_ir(tac1, quads1, "text"))
    
    # Example 2: Loops and conditionals
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Loops and Conditionals")
    print("=" * 70)
    
    ast2 = create_loop_example()
    generator2 = IRGenerator()
    tac2, quads2 = generator2.generate(ast2)
    
    print("\nGenerated IR:")
    print(format_ir(tac2, quads2, "text"))
    
    # Example 3: Array operations
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Array Operations")
    print("=" * 70)
    
    ast3 = create_array_example()
    generator3 = IRGenerator()
    tac3, quads3 = generator3.generate(ast3)
    
    print("\nGenerated IR:")
    print(format_ir(tac3, quads3, "text"))
    
    # Statistics
    print("\n" + "=" * 70)
    print("STATISTICS FOR ALL EXAMPLES")
    print("=" * 70)
    
    formatter = IRFormatter()
    
    print("\nExample 1 Statistics:")
    print(formatter.format_statistics(tac1, quads1))
    
    print("\nExample 2 Statistics:")
    print(formatter.format_statistics(tac2, quads2))
    
    print("\nExample 3 Statistics:")
    print(formatter.format_statistics(tac3, quads3))
    
    # Save output files
    print("\n" + "=" * 70)
    print("SAVING OUTPUT FILES")
    print("=" * 70)
    
    # Save JSON output
    with open("ir_output_example1.json", "w") as f:
        f.write(format_ir(tac1, quads1, "json"))
    print("✓ Saved: ir_output_example1.json")
    
    # Save HTML output
    with open("ir_output_example2.html", "w") as f:
        f.write(format_ir(tac2, quads2, "html"))
    print("✓ Saved: ir_output_example2.html")
    
    print("\n" + "=" * 70)
    print("EXAMPLES COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
