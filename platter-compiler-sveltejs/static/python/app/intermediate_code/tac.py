"""
Three Address Code (TAC) Representation for Platter Language

This module defines the TAC instruction classes used in intermediate representation.
Each TAC instruction has at most three addresses (operands).
"""

from typing import Optional, List, Any


class TACInstruction:
    """Base class for Three Address Code instructions"""
    def __init__(self, op_type: str):
        self.op_type = op_type
    
    def __repr__(self):
        return f"TAC({self.op_type})"


class TACAssignment(TACInstruction):
    """TAC for simple assignment: result = arg1"""
    def __init__(self, result: str, arg1: str):
        super().__init__("ASSIGN")
        self.result = result
        self.arg1 = arg1
    
    def __repr__(self):
        return f"{self.result} = {self.arg1}"


class TACBinaryOp(TACInstruction):
    """TAC for binary operation: result = arg1 op arg2"""
    def __init__(self, result: str, arg1: str, operator: str, arg2: str):
        super().__init__("BINOP")
        self.result = result
        self.arg1 = arg1
        self.operator = operator
        self.arg2 = arg2
    
    def __repr__(self):
        return f"{self.result} = {self.arg1} {self.operator} {self.arg2}"


class TACUnaryOp(TACInstruction):
    """TAC for unary operation: result = op arg1"""
    def __init__(self, result: str, operator: str, arg1: str):
        super().__init__("UNOP")
        self.result = result
        self.operator = operator
        self.arg1 = arg1
    
    def __repr__(self):
        return f"{self.result} = {self.operator} {self.arg1}"


class TACArrayAccess(TACInstruction):
    """TAC for array access: result = array[index]"""
    def __init__(self, result: str, array: str, index: str):
        super().__init__("ARRAY_READ")
        self.result = result
        self.array = array
        self.index = index
    
    def __repr__(self):
        return f"{self.result} = {self.array}[{self.index}]"


class TACArrayAssign(TACInstruction):
    """TAC for array assignment: array[index] = value"""
    def __init__(self, array: str, index: str, value: str):
        super().__init__("ARRAY_WRITE")
        self.array = array
        self.index = index
        self.value = value
    
    def __repr__(self):
        return f"{self.array}[{self.index}] = {self.value}"


class TACTableAccess(TACInstruction):
    """TAC for table field access: result = table.field"""
    def __init__(self, result: str, table: str, field: str):
        super().__init__("TABLE_READ")
        self.result = result
        self.table = table
        self.field = field
    
    def __repr__(self):
        return f"{self.result} = {self.table}.{self.field}"


class TACTableAssign(TACInstruction):
    """TAC for table field assignment: table.field = value"""
    def __init__(self, table: str, field: str, value: str):
        super().__init__("TABLE_WRITE")
        self.table = table
        self.field = field
        self.value = value
    
    def __repr__(self):
        return f"{self.table}.{self.field} = {self.value}"


class TACLabel(TACInstruction):
    """TAC label for control flow"""
    def __init__(self, label: str):
        super().__init__("LABEL")
        self.label = label
    
    def __repr__(self):
        return f"{self.label}:"


class TACGoto(TACInstruction):
    """TAC unconditional jump: goto label"""
    def __init__(self, label: str):
        super().__init__("GOTO")
        self.label = label
    
    def __repr__(self):
        return f"goto {self.label}"


class TACConditionalGoto(TACInstruction):
    """TAC conditional jump: if condition goto label"""
    def __init__(self, condition: str, label: str, negated: bool = False):
        super().__init__("IF_GOTO")
        self.condition = condition
        self.label = label
        self.negated = negated  # if False goto (ifFalse) vs if True goto (ifTrue)
    
    def __repr__(self):
        op = "ifFalse" if self.negated else "if"
        return f"{op} {self.condition} goto {self.label}"


class TACFunctionCall(TACInstruction):
    """TAC for function call: result = call func, n (where n is number of params)"""
    def __init__(self, result: Optional[str], func_name: str, num_params: int):
        super().__init__("CALL")
        self.result = result
        self.func_name = func_name
        self.num_params = num_params
    
    def __repr__(self):
        if self.result:
            return f"{self.result} = call {self.func_name}, {self.num_params}"
        return f"call {self.func_name}, {self.num_params}"


class TACParam(TACInstruction):
    """TAC for passing parameter: param arg"""
    def __init__(self, arg: str):
        super().__init__("PARAM")
        self.arg = arg
    
    def __repr__(self):
        return f"param {self.arg}"


class TACReturn(TACInstruction):
    """TAC for return statement: return [value]"""
    def __init__(self, value: Optional[str] = None):
        super().__init__("RETURN")
        self.value = value
    
    def __repr__(self):
        if self.value:
            return f"return {self.value}"
        return "return"


class TACFunctionBegin(TACInstruction):
    """TAC marking function beginning"""
    def __init__(self, func_name: str):
        super().__init__("FUNC_BEGIN")
        self.func_name = func_name
    
    def __repr__(self):
        return f"begin_func {self.func_name}"


class TACFunctionEnd(TACInstruction):
    """TAC marking function end"""
    def __init__(self, func_name: str):
        super().__init__("FUNC_END")
        self.func_name = func_name
    
    def __repr__(self):
        return f"end_func {self.func_name}"


class TACComment(TACInstruction):
    """TAC comment for readability"""
    def __init__(self, comment: str):
        super().__init__("COMMENT")
        self.comment = comment
    
    def __repr__(self):
        return f"# {self.comment}"


class TACAllocate(TACInstruction):
    """TAC for memory allocation (arrays, tables): result = allocate size"""
    def __init__(self, result: str, size: str, alloc_type: str):
        super().__init__("ALLOCATE")
        self.result = result
        self.size = size
        self.alloc_type = alloc_type  # "array" or "table"
    
    def __repr__(self):
        return f"{self.result} = allocate {self.alloc_type} {self.size}"


class TACCast(TACInstruction):
    """TAC for type casting: result = cast target_type arg"""
    def __init__(self, result: str, target_type: str, arg: str):
        super().__init__("CAST")
        self.result = result
        self.target_type = target_type
        self.arg = arg
    
    def __repr__(self):
        return f"{self.result} = ({self.target_type}) {self.arg}"


class TACNop(TACInstruction):
    """TAC no-operation (placeholder)"""
    def __init__(self):
        super().__init__("NOP")
    
    def __repr__(self):
        return "nop"
