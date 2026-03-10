"""
Integration Example: Complete Pipeline from Platter Source to IR

This demonstrates the complete compilation pipeline:
Platter Source → Lexer → Parser → AST → IR Generator → TAC + Quadruples

Usage:
    python ir_integration_example.py <platter_file>
    
    Or run with default example code
"""

import sys
import os

# Add parent directories to path
app_dir = os.path.dirname(os.path.dirname(__file__))
python_dir = os.path.dirname(app_dir)
sys.path.insert(0, python_dir)
sys.path.insert(0, app_dir)

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.intermediate_code import IRGenerator, IRFormatter


def compile_to_ir(source_code: str, verbose: bool = True):
    """
    Complete compilation pipeline from source to IR
    
    Args:
        source_code: Platter source code string
        verbose: If True, print intermediate steps
    
    Returns:
        (tac_instructions, quadruple_table, errors)
    """
    errors = []
    
    try:
        # Step 1: Lexical Analysis
        if verbose:
            print("=" * 70)
            print("STEP 1: LEXICAL ANALYSIS")
            print("=" * 70)
        
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        if verbose:
            print(f"[OK] Generated {len(tokens)} tokens")
            print("\nFirst 10 tokens:")
            for i, token in enumerate(tokens[:10]):
                print(f"  {i}: {token}")
        
        # Step 2: Syntax Analysis (Parsing)
        if verbose:
            print("\n" + "=" * 70)
            print("STEP 2: SYNTAX ANALYSIS (PARSING)")
            print("=" * 70)
        
        parser = ASTParser(tokens)
        ast = parser.parse_program()
        
        if verbose:
            print(f"[OK] AST constructed successfully")
            print(f"  - Global declarations: {len(ast.global_decl)}")
            print(f"  - Recipe declarations: {len(ast.recipe_decl)}")
            print(f"  - Has start platter: {'Yes' if ast.start_platter else 'No'}")
        
        # Step 3: Intermediate Code Generation
        if verbose:
            print("\n" + "=" * 70)
            print("STEP 3: INTERMEDIATE CODE GENERATION")
            print("=" * 70)
        
        ir_generator = IRGenerator()
        tac_instructions, quadruple_table = ir_generator.generate(ast)
        
        if verbose:
            print(f"[OK] IR generated successfully")
            print(f"  - TAC instructions: {len(tac_instructions)}")
            print(f"  - Quadruples: {len(quadruple_table)}")
            print(f"  - Temporary variables: {ir_generator.temp_count}")
            print(f"  - Labels: {ir_generator.label_count}")
        
        return tac_instructions, quadruple_table, None
        
    except Exception as e:
        errors.append(str(e))
        if verbose:
            print(f"\n[ERROR] Compilation failed with error: {e}")
        return None, None, errors


def main():
    """Main function"""
    
    # Default example Platter code
    default_code = """
start() {
    piece of x = 5;
    piece of y = 10;
    piece of sum = 0;
    
    piece of i = 0;
    sum = x + y;
    
    check (sum > 10) {
        x = x + 1;
    }
    
    repeat (i < 5) {
        sum = sum + i;
        i = i + 1;
    }
    
    serve sum;
}
    """
    
    # Check if file provided
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        try:
            with open(filepath, 'r') as f:
                source_code = f.read()
            print(f"Reading from file: {filepath}")
        except FileNotFoundError:
            print(f"Error: File '{filepath}' not found")
            print("Using default example code instead\n")
            source_code = default_code
    else:
        print("No file provided, using default example code\n")
        source_code = default_code
    
    print("=" * 70)
    print("PLATTER COMPILER - COMPLETE PIPELINE TO IR")
    print("=" * 70)
    print("\nSOURCE CODE:")
    print("-" * 70)
    print(source_code)
    print("-" * 70)
    
    # Compile to IR
    tac, quads, errors = compile_to_ir(source_code, verbose=True)
    
    if errors:
        print("\n" + "=" * 70)
        print("COMPILATION ERRORS")
        print("=" * 70)
        for error in errors:
            print(f"  [ERROR] {error}")
        return
    
    # Display results
    print("\n" + "=" * 70)
    print("INTERMEDIATE REPRESENTATION OUTPUT")
    print("=" * 70)
    
    formatter = IRFormatter()
    
    # TAC
    print("\n" + formatter.format_tac_text(tac))
    
    # Quadruples (readable)
    print("\n" + formatter.format_quadruples_readable(quads))
    
    # Statistics
    print("\n" + formatter.format_statistics(tac, quads))
    
    # Save outputs
    print("\n" + "=" * 70)
    print("SAVING OUTPUT FILES")
    print("=" * 70)
    
    # Save text output
    with open("ir_output.txt", "w") as f:
        f.write(formatter.format_both_text(tac, quads))
    print("[OK] Saved: ir_output.txt")
    
    # Save JSON output
    with open("ir_output.json", "w") as f:
        f.write(formatter.format_both_json(tac, quads))
    print("[OK] Saved: ir_output.json")
    
    # Save HTML output
    with open("ir_output.html", "w") as f:
        f.write(formatter.format_html(tac, quads))
    print("[OK] Saved: ir_output.html")
    
    print("\n" + "=" * 70)
    print("COMPILATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    main()
