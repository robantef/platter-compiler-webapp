# INTERMEDIATE REPRESENTATION QUICK REFERENCE

## Three Address Code (TAC) Instructions

### Assignment Operations
```
result = arg1                    # Simple assignment
result = arg1 op arg2           # Binary operation
result = op arg1                # Unary operation
```

### Arithmetic & Logical Operations
```
t1 = a + b                      # Addition
t2 = a - b                      # Subtraction
t3 = a * b                      # Multiplication
t4 = a / b                      # Division
t5 = a % b                      # Modulo
t6 = -a                         # Unary minus
t7 = not a                      # Logical NOT
t8 = a and b                    # Logical AND
t9 = a or b                     # Logical OR
```

### Comparison Operations
```
t1 = a == b                     # Equal
t2 = a != b                     # Not equal
t3 = a < b                      # Less than
t4 = a > b                      # Greater than
t5 = a <= b                     # Less than or equal
t6 = a >= b                     # Greater than or equal
```

### Array Operations
```
t1 = arr[i]                     # Array read
arr[i] = value                  # Array write
arr = allocate array size       # Array allocation
```

### Table/Struct Operations
```
t1 = table.field                # Table field read
table.field = value             # Table field write
table = allocate table type     # Table allocation
```

### Control Flow
```
L1:                             # Label
goto L2                         # Unconditional jump
if condition goto L3            # Conditional jump (if true)
ifFalse condition goto L4       # Conditional jump (if false)
```

### Function Operations
```
param arg1                      # Push parameter
param arg2
t1 = call func, 2              # Function call (2 params)
return value                    # Return with value
return                          # Return void
```

### Function Markers
```
begin_func function_name        # Function start
end_func function_name          # Function end
```

### Type Casting
```
t1 = (piece) value             # Cast to piece (int)
t2 = (sip) value               # Cast to sip (float)
t3 = (flag) value              # Cast to flag (bool)
t4 = (chars) value             # Cast to chars (string)
```

### Other
```
# Comment text                  # Comment
nop                            # No operation
```

---

## Quadruple Format

### Structure
```
(operator, arg1, arg2, result)
```

### Binary Operations
```
(+, a, b, t1)                  # t1 = a + b
(-, a, b, t2)                  # t2 = a - b
(*, a, b, t3)                  # t3 = a * b
(/, a, b, t4)                  # t4 = a / b
(%, a, b, t5)                  # t5 = a % b
```

### Comparison Operations
```
(==, a, b, t1)                 # t1 = a == b
(!=, a, b, t2)                 # t2 = a != b
(<, a, b, t3)                  # t3 = a < b
(>, a, b, t4)                  # t4 = a > b
(<=, a, b, t5)                 # t5 = a <= b
(>=, a, b, t6)                 # t6 = a >= b
```

### Logical Operations
```
(and, a, b, t1)                # t1 = a and b
(or, a, b, t2)                 # t2 = a or b
(not, a, -, t3)                # t3 = not a
(unary-, a, -, t4)             # t4 = -a
```

### Assignment
```
(=, value, -, var)             # var = value
```

### Array Operations
```
([], arr, index, t1)           # t1 = arr[index]
([]=, arr, index, value)       # arr[index] = value
(allocate, array, size, arr)   # arr = allocate array size
```

### Table Operations
```
(., table, field, t1)          # t1 = table.field
(.=, table, field, value)      # table.field = value
(allocate, table, type, tbl)   # tbl = allocate table type
```

### Control Flow
```
(label, L1, -, -)              # L1:
(goto, -, -, L2)               # goto L2
(if, cond, -, L3)              # if cond goto L3
(ifFalse, cond, -, L4)         # ifFalse cond goto L4
```

### Function Operations
```
(param, arg, -, -)             # param arg
(call, func, n, result)        # result = call func, n
(call, func, n, -)             # call func, n (void)
(return, value, -, -)          # return value
(return, -, -, -)              # return
(begin_func, name, -, -)       # begin_func name
(end_func, name, -, -)         # end_func name
```

### Type Casting
```
(cast, type, value, result)    # result = (type) value
```

### Comment
```
(comment, text, -, -)          # # text
```

---

## Example: Complete IR for Simple Program

### Platter Source
```platter
piece x = 5;
piece y = 10;

start() {
    piece sum = x + y;
    piece product = x * y;
}
```

### TAC Output
```
0   : # === Platter Program IR ===
1   : # Global Declarations
2   : x = 5
3   : y = 10
4   : # Main Program (start)
5   : begin_func start
6   : t0 = x + y
7   : sum = t0
8   : t1 = x * y
9   : product = t1
10  : end_func start
```

### Quadruple Output (Tabular)
```
Index  Operator     Arg1         Arg2         Result      
--------------------------------------------------------------
0      comment      Global De    -            -           
1      =            5            -            x           
2      =            10           -            y           
3      comment      Main Prog    -            -           
4      begin_func   start        -            -           
5      +            x            y            t0          
6      =            t0           -            sum         
7      *            x            y            t1          
8      =            t1           -            product     
9      end_func     start        -            -           
```

### Quadruple Output (Readable)
```
0   : # Global Declarations
1   : x = 5
2   : y = 10
3   : # Main Program (start)
4   : begin_func start
5   : t0 = x + y
6   : sum = t0
7   : t1 = x * y
8   : product = t1
9   : end_func start
```

---

## Control Flow Examples

### If Statement
```platter
check (x > 5) {
    y = 1;
} instead {
    y = 0;
}
```

**TAC:**
```
t1 = x > 5
ifFalse t1 goto L0_else
y = 1
goto L0_endif
L0_else:
y = 0
L0_endif:
```

### While Loop
```platter
repeat (i < 10) {
    sum = sum + i;
    i = i + 1;
}
```

**TAC:**
```
L0_while_start:
t1 = i < 10
ifFalse t1 goto L0_while_end
t2 = sum + i
sum = t2
t3 = i + 1
i = t3
goto L0_while_start
L0_while_end:
```

### For Loop
```platter
pass (i = 0; i < 10; i = i + 1) {
    sum = sum + i;
}
```

**TAC:**
```
i = 0
L0_for_start:
t1 = i < 10
ifFalse t1 goto L0_for_end
t2 = sum + i
sum = t2
L0_for_continue:
t3 = i + 1
i = t3
goto L0_for_start
L0_for_end:
```

### Function Call
```platter
recipe piece add(piece a, piece b) {
    serve a + b;
}

start() {
    piece result = add(5, 3);
}
```

**TAC:**
```
# Recipe: add
begin_func add
t0 = a + b
return t0
end_func add

# Main Program (start)
begin_func start
param 5
param 3
t1 = call add, 2
result = t1
end_func start
```

---

## Temporary Variables

- **Format**: `t0`, `t1`, `t2`, ...
- **Purpose**: Hold intermediate computation results
- **Lifetime**: Local to current function/scope
- **Generation**: Automatic, sequential numbering

## Labels

- **Format**: `L0`, `L1`, `L2`, ... or `prefix_name0`, `prefix_name1`, ...
- **Purpose**: Control flow targets
- **Types**:
  - `while_start`, `while_end` - While loop labels
  - `for_start`, `for_continue`, `for_end` - For loop labels  
  - `do_start`, `do_continue`, `do_end` - Do-while loop labels
  - `if_else`, `if_endif` - Conditional labels
  - `case`, `default`, `switch_end` - Switch labels

---

## Platter Type Mapping

| Platter Type | Description | Example Values |
|--------------|-------------|----------------|
| `piece`      | Integer     | `42`, `-10`, `0` |
| `sip`        | Float       | `3.14`, `-0.5` |
| `flag`       | Boolean     | `true`, `false` |
| `chars`      | String      | `"hello"` |
| `piece[]`    | Int Array   | `[1, 2, 3]` |
| `table`      | Structure   | Custom types |

---

## Implementation Notes

1. **Single Pass**: IR generated in one traversal of AST
2. **No Optimization**: Direct translation, optimizations in separate pass
3. **Explicit Temporaries**: All intermediate values stored in temps
4. **Structured Control Flow**: Uses labels and gotos
5. **Function Calling**: Standard param-call-return sequence
6. **Memory Model**: Simplified allocation for arrays/tables

---

## Files Reference

- `tac.py` - TAC instruction classes
- `quadruple.py` - Quadruple definitions
- `ir_generator.py` - Main IR generator
- `output_formatter.py` - Output formatting
- `example_usage.py` - Usage examples
- `ir_integration_example.py` - Full pipeline demo
- `README.md` - Complete documentation

---

**Last Updated**: February 2026  
**Version**: 1.0.0
