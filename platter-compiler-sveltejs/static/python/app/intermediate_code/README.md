# Intermediate Code Generator for Platter Language

This module provides a complete implementation of intermediate representation (IR) generation for the Platter programming language. It generates both **Three Address Code (TAC)** and **Quadruples** from the Abstract Syntax Tree (AST).

## Overview

The intermediate code generator is a crucial phase in the compilation process that:
- Transforms high-level AST into low-level IR
- Generates temporary variables for intermediate results
- Creates labels for control flow
- Produces both TAC and Quadruple representations simultaneously

## Components

### 1. **tac.py** - Three Address Code Instructions

Defines all TAC instruction types:
- `TACAssignment` - Simple assignments
- `TACBinaryOp` - Binary operations (+, -, *, /, etc.)
- `TACUnaryOp` - Unary operations (-, not)
- `TACArrayAccess` / `TACArrayAssign` - Array operations
- `TACTableAccess` / `TACTableAssign` - Table/struct operations
- `TACLabel` / `TACGoto` / `TACConditionalGoto` - Control flow
- `TACFunctionCall` / `TACParam` / `TACReturn` - Function calls
- `TACAllocate` - Memory allocation
- `TACCast` - Type casting
- `TACComment` - Comments for readability

### 2. **quadruple.py** - Quadruple Representation

Defines the quadruple structure `(operator, arg1, arg2, result)`:
- `Quadruple` - Individual quadruple
- `QuadrupleTable` - Container for all quadruples with indexing
- Helper functions for creating common quadruple types
- Backpatching support for forward references

### 3. **ir_generator.py** - Main IR Generator

The core generator that traverses the AST and produces IR:
- Visitor pattern for AST traversal
- Temporary variable management
- Label generation for control flow
- Handles all statement types (if, loops, switch, etc.)
- Handles all expression types (binary, unary, calls, etc.)

### 4. **output_formatter.py** - Output Formatting

Provides multiple output formats:
- Plain text (readable and tabular)
- JSON (for programmatic access)
- HTML (for web viewing)
- Statistics generation

### 5. **example_usage.py** - Examples and Tests

Demonstrates how to use the IR generator with sample programs.

## Installation

No external dependencies required. The module uses only Python standard library.

## Usage

### Basic Usage

```python
from semantic_analyzer.ast.ast_parser_program import ASTParser
from intermediate_code import IRGenerator, format_ir

# Parse your Platter code to get AST
# (assuming you have tokens from lexer)
parser = ASTParser(tokens)
ast = parser.parse_program()

# Generate intermediate representation
generator = IRGenerator()
tac_instructions, quadruple_table = generator.generate(ast)

# Format and display
print(format_ir(tac_instructions, quadruple_table, format_type="text"))
```

### Advanced Usage

```python
from intermediate_code import IRGenerator, IRFormatter

# Generate IR
generator = IRGenerator()
tac, quads = generator.generate(ast)

# Use custom formatter
formatter = IRFormatter()

# Text output
print(formatter.format_tac_text(tac))
print(formatter.format_quadruples_readable(quads))

# JSON output
json_output = formatter.format_both_json(tac, quads)

# HTML output
html_output = formatter.format_html(tac, quads)

# Statistics
stats = formatter.format_statistics(tac, quads)
print(stats)
```

## Three Address Code (TAC) Format

Each TAC instruction has at most three addresses:

```
result = arg1 op arg2    # Binary operation
result = op arg1         # Unary operation
result = arg1            # Assignment
if condition goto L1     # Conditional jump
goto L2                  # Unconditional jump
L1:                      # Label
param arg1               # Function parameter
result = call func, n    # Function call
return result            # Return statement
```

## Quadruple Format

Each quadruple is a tuple: `(operator, arg1, arg2, result)`

Examples:
```
(+, a, b, t1)           # t1 = a + b
(=, t1, -, x)           # x = t1
(ifFalse, t2, -, L1)    # if !t2 goto L1
(goto, -, -, L2)        # goto L2
([], arr, i, t3)        # t3 = arr[i]
([]=, arr, i, val)      # arr[i] = val
```

## Supported Language Features

### Declarations
- ✅ Variable declarations (with/without initialization)
- ✅ Array declarations
- ✅ Table (struct) declarations
- ✅ Table prototype definitions
- ✅ Function (recipe) declarations

### Statements
- ✅ Assignment (=, +=, -=, *=, /=, %=)
- ✅ If-else-elif statements
- ✅ While loops
- ✅ Do-while loops
- ✅ For loops
- ✅ Switch-case statements
- ✅ Break and continue
- ✅ Return statements
- ✅ Expression statements

### Expressions
- ✅ Binary operations (+, -, *, /, %, ==, !=, <, >, <=, >=, and, or)
- ✅ Unary operations (-, not)
- ✅ Variable references
- ✅ Literals (piece, sip, flag, chars)
- ✅ Array access
- ✅ Table field access
- ✅ Function calls
- ✅ Type casting
- ✅ Array literals
- ✅ Table literals

## Control Flow Handling

The generator correctly handles:
- **If statements**: Generates labels and conditional jumps
- **Loops**: Generates start, continue, and end labels
- **Break/Continue**: Jumps to appropriate labels
- **Switch**: Generates comparison chain with case labels
- **Nested structures**: Maintains loop stack for correct break/continue

## Temporary Variables

- Naming: `t0, t1, t2, ...`
- Generated for intermediate expression results
- Automatically managed and unique

## Labels

- Naming: `L0, L1, L2, ...` or with prefixes like `while_start0`, `if_end1`
- Generated for control flow targets
- Support for backpatching (forward references)

## Output Examples

### TAC Example
```
0   : # === Platter Program IR ===
1   : # Main Program (start)
2   : begin_func start
3   : t0 = 5
4   : t1 = 3
5   : param t0
6   : param t1
7   : t2 = call add, 2
8   : result = t2
9   : end_func start
```

### Quadruple Example (Tabular)
```
Index  Operator     Arg1         Arg2         Result      
--------------------------------------------------------------
0      comment      Platter Pr   -            -           
1      begin_func   start        -            -           
2      =            5            -            t0          
3      =            3            -            t1          
4      param        t0           -            -           
5      param        t1           -            -           
6      call         add          2            t2          
7      =            t2           -            result      
8      end_func     start        -            -           
```

### Quadruple Example (Readable)
```
0   : # Platter Program IR
1   : begin_func start
2   : t0 = 5
3   : t1 = 3
4   : param t0
5   : param t1
6   : t2 = call add, 2
7   : result = t2
8   : end_func start
```

## Testing

Run the example file to test the generator:

```bash
cd intermediate_code
python example_usage.py
```

This will:
1. Create sample ASTs
2. Generate IR for each
3. Display TAC and Quadruples
4. Generate statistics
5. Save JSON and HTML outputs

## Integration with Compiler Pipeline

```
Source Code
    ↓
[Lexer] → Tokens
    ↓
[Parser] → AST
    ↓
[Semantic Analyzer] → Annotated AST (optional)
    ↓
[IR Generator] → TAC + Quadruples ← YOU ARE HERE
    ↓
[Optimizer] → Optimized IR (future)
    ↓
[Code Generator] → Target Code (future)
```

## Future Enhancements

- [ ] Optimization passes (constant folding, dead code elimination)
- [ ] Control flow graph (CFG) generation
- [ ] Data flow analysis
- [ ] Register allocation hints
- [ ] Target-specific code generation

## Error Handling

Currently, the IR generator assumes a valid AST input. For production use, add:
- Type checking validation
- Undefined variable detection
- Array bounds analysis
- Function signature verification

## Performance

- Time Complexity: O(n) where n is number of AST nodes
- Space Complexity: O(n) for TAC and Quadruple storage
- Optimized for single-pass generation

## Authors

Platter Compiler Team - BSCS 3-3 (2025)

## License

See LICENSE file in project root.

---

**Note**: This intermediate code generator is designed specifically for the Platter language and integrates seamlessly with the existing lexer, parser, and semantic analyzer modules.
