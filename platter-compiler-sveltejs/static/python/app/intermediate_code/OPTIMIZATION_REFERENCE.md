# Code Optimization Module

This module provides comprehensive code optimization capabilities for the Platter compiler's intermediate representation (IR).

## Overview

The optimization module implements various optimization passes that improve the quality of generated code by:
- Reducing code size
- Improving execution speed
- Eliminating redundant operations
- Simplifying expressions

## Architecture

The optimization system is built on a modular architecture:

```
optimizer.py               # Base classes for optimization infrastructure
├── OptimizationPass      # Abstract base class for all passes
├── BasicBlock            # Represents a basic block with data flow sets
└── ControlFlowGraph      # CFG builder and liveness analysis

optimization passes/
├── constant_folding.py           # Compile-time constant evaluation
├── propagation.py                # Constant and copy propagation
├── dead_code_elimination.py      # Dead and unreachable code removal
└── algebraic_simplification.py   # Algebraic identities and strength reduction

optimizer_manager.py      # Coordinates multiple passes
```

## Optimization Passes

### 1. Constant Folding

**Purpose**: Evaluate expressions with constant operands at compile time.

**Examples**:
```
Before:              After:
t1 = 2 + 3          t1 = 5
t2 = 10 * 2         t2 = 20
t3 = 5 > 3          t3 = true
```

**Supported Operations**:
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparisons: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Boolean: `and`, `or`, `not`
- Unary: `-`, `not`

### 2. Constant Propagation

**Purpose**: Replace variable uses with known constant values.

**Example**:
```
Before:              After:
x = 5               x = 5
y = x + 3           y = 5 + 3        # Propagated x
                    y = 8             # Then folded
```

**Algorithm**: Forward data flow analysis tracking constant assignments.

### 3. Copy Propagation

**Purpose**: Replace variable uses with the original variable from copy assignments.

**Example**:
```
Before:              After:
x = 10              x = 10
y = x               # Eliminated
z = y + 5           z = x + 5         # Use x instead of y
```

**Algorithm**: Tracks copy assignments and propagates the original variable.

### 4. Dead Code Elimination

**Purpose**: Remove unused assignments and unreachable code.

**Examples**:

*Dead Assignment*:
```
Before:              After:
t1 = 5              # Removed (t1 never used)
x = 10              x = 10
y = x + 1           y = x + 1
```

*Unreachable Code*:
```
Before:              After:
return x            return x
y = 5               # Removed (unreachable)
```

**Algorithm**: 
- Backward pass to collect used variables
- Forward pass to remove dead assignments
- Removes code after unconditional jumps and returns

### 5. Unreachable Code Elimination

**Purpose**: Remove code blocks that can never be executed.

**Algorithm**: 
- Build Control Flow Graph (CFG)
- Perform depth-first search from entry block
- Remove blocks not visited

### 6. Algebraic Simplification

**Purpose**: Apply algebraic identities to simplify expressions.

**Identity Rules**:

| Operation | Pattern | Simplification |
|-----------|---------|---------------|
| Addition | `x + 0` | `x` |
| | `0 + x` | `x` |
| Subtraction | `x - 0` | `x` |
| | `x - x` | `0` |
| | `0 - x` | `-x` |
| Multiplication | `x * 1` | `x` |
| | `1 * x` | `x` |
| | `x * 0` | `0` |
| | `0 * x` | `0` |
| Division | `x / 1` | `x` |
| | `x / x` | `1` |
| | `0 / x` | `0` |
| Modulo | `x % 1` | `0` |
| | `x % x` | `0` |
| Boolean AND | `x and true` | `x` |
| | `x and false` | `false` |
| Boolean OR | `x or false` | `x` |
| | `x or true` | `true` |

### 7. Strength Reduction

**Purpose**: Replace expensive operations with cheaper equivalents.

**Examples**:
```
Before:              After:
x = y * 2           x = y + y          # Addition cheaper than multiply
```

**Potential Optimizations**:
- `x * 2` → `x + x`
- `x ** 2` → `x * x`
- Multiplication by power of 2 → left shift
- Division by power of 2 → right shift

## Optimizer Manager

The `OptimizerManager` coordinates multiple passes and applies them iteratively.

### Optimization Levels

```python
OptimizationLevel.NONE        # O0 - No optimization
OptimizationLevel.BASIC       # O1 - Basic optimizations
OptimizationLevel.STANDARD    # O2 - Standard optimizations (default)
OptimizationLevel.AGGRESSIVE  # O3 - Maximum optimization
```

### Configuration by Level

**O0 (None)**:
- No optimizations applied

**O1 (Basic)**:
- Constant Folding
- Dead Code Elimination

**O2 (Standard)**:
- All O1 optimizations
- Algebraic Simplification
- Constant Propagation
- Copy Propagation
- Dead Code Elimination (repeated)

**O3 (Aggressive)**:
- All O2 optimizations
- Strength Reduction
- Unreachable Code Elimination (CFG-based)

### Iterative Optimization

The manager applies passes iteratively until a fixed point is reached (no more changes) or the maximum iteration limit is hit.

```python
for iteration in range(max_iterations):
    changes = 0
    for pass in passes:
        changes += apply_pass(pass)
    if changes == 0:
        break  # Fixed point reached
```

## Usage

### Basic Usage

```python
from app.intermediate_code import (
    IRGenerator,
    OptimizerManager,
    OptimizationLevel
)

# Generate IR from AST
ir_gen = IRGenerator()
ir_gen.generate(ast)

# Optimize
manager = OptimizerManager(OptimizationLevel.STANDARD)
optimized_tac = manager.optimize_tac(ir_gen.instructions)
optimized_quads = manager.optimize_quads(ir_gen.quad_table)

# Print statistics
manager.print_stats()
```

### Using Individual Passes

```python
from app.intermediate_code import ConstantFoldingPass

# Apply single pass
pass_obj = ConstantFoldingPass()
optimized = pass_obj.optimize_tac(instructions)

print(f"Changes made: {pass_obj.changes_made}")
```

### Custom Pass Pipeline

```python
from app.intermediate_code import (
    OptimizerManager,
    OptimizationLevel,
    ConstantFoldingPass,
    DeadCodeEliminationPass
)

# Create custom pipeline
manager = OptimizerManager(OptimizationLevel.NONE)  # Start empty
manager.add_pass(ConstantFoldingPass())
manager.add_pass(DeadCodeEliminationPass())

optimized = manager.optimize_tac(instructions)
```

### Convenience Function

```python
from app.intermediate_code import optimize_ir, OptimizationLevel

# Optimize both TAC and quadruples
optimized_tac, optimized_quads, stats = optimize_ir(
    instructions=tac_instructions,
    quad_table=quad_table,
    level=OptimizationLevel.AGGRESSIVE,
    verbose=True  # Print statistics
)
```

## Statistics and Reporting

The optimizer tracks detailed statistics:

```python
manager.get_stats()
# Returns:
# {
#     'total_iterations': 3,
#     'total_changes': 15,
#     'original_size': 50,
#     'optimized_size': 35,
#     'ConstantFoldingPass': {
#         'changes': 8,
#         'applications': 3
#     },
#     ...
# }

manager.print_stats()
# Prints formatted statistics report
```

**Sample Output**:
```
============================================================
OPTIMIZATION STATISTICS
============================================================

Optimization Level: Standard (O2)
Total Iterations: 2
Total Changes: 12
Original Size: 45 instructions
Optimized Size: 33 instructions
Reduction: 12 instructions (26.7%)

Per-Pass Statistics:
------------------------------------------------------------
  Constant Folding:
    Changes: 5
    Applications: 2
  Dead Code Elimination:
    Changes: 4
    Applications: 2
  Algebraic Simplification:
    Changes: 3
    Applications: 2
============================================================
```

## Examples

See [optimization_examples.py](optimization_examples.py) for comprehensive examples demonstrating:

1. Constant Folding
2. Dead Code Elimination
3. Algebraic Simplification
4. Copy Propagation
5. Combined Optimizations

Run examples:
```bash
python optimization_examples.py
```

## Implementation Details

### Data Flow Analysis

The optimizer uses data flow analysis for optimizations:

1. **Use-Def Analysis**: Track where variables are used and defined
2. **Liveness Analysis**: Determine which variables are live at each point
3. **Reaching Definitions**: Track which definitions reach each use

### Basic Blocks

A basic block is a maximal sequence of instructions with:
- Single entry point (first instruction)
- Single exit point (last instruction)
- No internal branches

Properties tracked per block:
- `use`: Variables used before definition in block
- `def_`: Variables defined in block
- `in_`: Variables live at block entry
- `out`: Variables live at block exit

### Control Flow Graph

The CFG represents program control flow:
- Nodes: Basic blocks
- Edges: Control flow between blocks

Used for:
- Liveness analysis
- Reachability analysis
- Loop detection

## Extending the Optimizer

### Creating a Custom Pass

```python
from app.intermediate_code.optimizer import OptimizationPass
from app.intermediate_code.tac import TACInstruction
from typing import List

class MyCustomPass(OptimizationPass):
    def __init__(self):
        super().__init__("My Custom Optimization")
    
    def optimize_tac(self, instructions: List[TACInstruction]):
        self.reset_stats()
        optimized = []
        
        for instr in instructions:
            # Your optimization logic here
            if should_optimize(instr):
                new_instr = optimize_instruction(instr)
                optimized.append(new_instr)
                self.changes_made += 1
            else:
                optimized.append(instr)
        
        return optimized
    
    def optimize_quads(self, quad_table):
        # Quadruple optimization logic
        return quad_table
```

## Performance Considerations

- **Fixed Point Iteration**: Most programs reach fixed point in 2-3 iterations
- **Pass Ordering**: Order matters - some passes enable others
- **Time Complexity**: O(n) per pass for most optimizations
- **Space Complexity**: O(n) for temporary data structures

## Future Enhancements

Potential future optimizations:

1. **Common Subexpression Elimination**: Eliminate redundant computations
2. **Loop Optimizations**:
   - Loop invariant code motion
   - Loop unrolling
   - Loop fusion
3. **Inline Expansion**: Inline small functions
4. **Register Allocation**: Minimize memory access
5. **Peephole Optimization**: Local instruction pattern matching
6. **Tail Call Optimization**: Convert recursion to iteration

## References

- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools*. Pearson.
- Cooper, K. D., & Torczon, L. (2011). *Engineering a Compiler*. Morgan Kaufmann.

## Version

Current Version: 1.0.0

## Authors

Platter Compiler Team
