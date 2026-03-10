"""
Optimization Examples

Demonstrates various optimization passes on actual Platter code.
"""

import sys
import os

# Add parent directories to path
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
python_dir = os.path.dirname(app_dir)
sys.path.insert(0, python_dir)
sys.path.insert(0, app_dir)

from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.intermediate_code.ir_generator import IRGenerator
from app.intermediate_code.output_formatter import IRFormatter
from app.intermediate_code.optimizer_manager import OptimizerManager, OptimizationLevel, optimize_ir


def example_constant_folding():
    """Example showing constant folding"""
    print("\n" + "="*80)
    print("EXAMPLE 1: CONSTANT FOLDING")
    print("="*80)
    
    source_code = """
start() {
    piece of x = 2 + 3;
    piece of y = 10 * 2;
    piece of z = x + 5;
}
    """
    
    print("\nSource Code:")
    print(source_code)
    
    # Parse and generate IR
    instructions, quads, _ = compile_to_ir(source_code)
    
    print("\n[BEFORE OPTIMIZATION]")
    print_tac(instructions)
    
    # Optimize
    manager = OptimizerManager(OptimizationLevel.STANDARD)
    optimized = manager.optimize_tac(instructions)
    
    print("\n[AFTER OPTIMIZATION]")
    print_tac(optimized)
    manager.print_stats()


def example_dead_code_elimination():
    """Example showing dead code elimination"""
    print("\n" + "="*80)
    print("EXAMPLE 2: DEAD CODE ELIMINATION")
    print("="*80)
    
    source_code = """
start() {
    piece of x = 5;
    piece of y = 10;
    piece of z = x + 1;
    serve z;
}
    """
    
    print("\nSource Code:")
    print(source_code)
    
    instructions, quads, _ = compile_to_ir(source_code)
    
    print("\n[BEFORE OPTIMIZATION]")
    print_tac(instructions)
    
    manager = OptimizerManager(OptimizationLevel.STANDARD)
    optimized = manager.optimize_tac(instructions)
    
    print("\n[AFTER OPTIMIZATION]")
    print_tac(optimized)
    manager.print_stats()


def example_algebraic_simplification():
    """Example showing algebraic simplification"""
    print("\n" + "="*80)
    print("EXAMPLE 3: ALGEBRAIC SIMPLIFICATION")
    print("="*80)
    
    source_code = """
start() {
    piece of x = 5;
    piece of y = x + 0;
    piece of z = y * 1;
    piece of w = z - 0;
    serve w;
}
    """
    
    print("\nSource Code:")
    print(source_code)
    
    instructions, quads, _ = compile_to_ir(source_code)
    
    print("\n[BEFORE OPTIMIZATION]")
    print_tac(instructions)
    
    manager = OptimizerManager(OptimizationLevel.STANDARD)
    optimized = manager.optimize_tac(instructions)
    
    print("\n[AFTER OPTIMIZATION]")
    print_tac(optimized)
    manager.print_stats()


def example_copy_propagation():
    """Example showing copy propagation"""
    print("\n" + "="*80)
    print("EXAMPLE 4: COPY PROPAGATION")
    print("="*80)
    
    source_code = """
start() {
    piece of a = 10;
    piece of b = a;
    piece of c = b + 5;
    serve c;
}
    """
    
    print("\nSource Code:")
    print(source_code)
    
    instructions, quads, _ = compile_to_ir(source_code)
    
    print("\n[BEFORE OPTIMIZATION]")
    print_tac(instructions)
    
    manager = OptimizerManager(OptimizationLevel.STANDARD)
    optimized = manager.optimize_tac(instructions)
    
    print("\n[AFTER OPTIMIZATION]")
    print_tac(optimized)
    manager.print_stats()


def example_combined_optimizations():
    """Example showing multiple optimizations working together"""
    print("\n" + "="*80)
    print("EXAMPLE 5: COMBINED OPTIMIZATIONS")
    print("="*80)
    
    source_code = """
start() {
    piece of n = 7;
    piece of result = n * 1 + 0;
    piece of temp = 5 + 3;
    piece of unused = 100;
    piece of final = result + temp;
    serve final;
}
    """
    
    print("\nSource Code:")
    print(source_code)
    
    instructions, quads, _ = compile_to_ir(source_code)
    
    print("\n[BEFORE OPTIMIZATION]")
    print_tac(instructions)
    
    # Try different optimization levels
    for level in [OptimizationLevel.BASIC, OptimizationLevel.STANDARD, OptimizationLevel.AGGRESSIVE]:
        manager = OptimizerManager(level)
        optimized = manager.optimize_tac(instructions)
        
        print(f"\n[OPTIMIZATION LEVEL: {manager._get_level_name()}]")
        print_tac(optimized)
        manager.print_stats()


def compile_to_ir(source_code: str):
    """Compile source code to IR"""
    try:
        # Lexer
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Parser
        ast_parser = ASTParser(tokens)
        ast = ast_parser.parse_program()
        
        # IR Generation
        ir_gen = IRGenerator()
        instructions, quad_table = ir_gen.generate(ast)
        
        return instructions, quad_table, ir_gen
        
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        return None, None, None


def print_tac(instructions):
    """Print TAC instructions in readable format"""
    for i, instr in enumerate(instructions):
        print(f"  {i:3d}: {instr}")


def main():
    """Run all examples"""
    print("\n")
    print("*" * 80)
    print("*" + " " * 78 + "*")
    print("*" + "PLATTER COMPILER - CODE OPTIMIZATION EXAMPLES".center(78) + "*")
    print("*" + " " * 78 + "*")
    print("*" * 80)
    
    try:
        example_constant_folding()
        example_dead_code_elimination()
        example_algebraic_simplification()
        example_copy_propagation()
        example_combined_optimizations()
        
        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
