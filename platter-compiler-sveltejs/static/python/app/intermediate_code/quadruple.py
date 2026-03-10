"""
Quadruple Representation for Platter Language

This module defines the Quadruple structure used in intermediate representation.
A quadruple has the form (operator, arg1, arg2, result).
"""

from typing import Optional, List


class Quadruple:
    """
    Quadruple representation: (operator, arg1, arg2, result)
    
    Different instruction types use the fields differently:
    - Binary ops: (op, arg1, arg2, result) -> result = arg1 op arg2
    - Unary ops: (op, arg1, -, result) -> result = op arg1
    - Assignment: (=, arg1, -, result) -> result = arg1
    - Conditional: (ifFalse, condition, -, label) -> if !condition goto label
    - Unconditional: (goto, -, -, label) -> goto label
    - Function call: (call, func, n_params, result) -> result = call func(n_params)
    - Param: (param, arg, -, -) -> push param arg
    - Return: (return, value, -, -) -> return value
    - Label: (label, name, -, -) -> name:
    - Array read: ([], array, index, result) -> result = array[index]
    - Array write: ([]=, array, index, value) -> array[index] = value
    - Table read: (., table, field, result) -> result = table.field
    - Table write: (.=, table, field, value) -> table.field = value
    """
    
    def __init__(self, operator: str, arg1: Optional[str] = None, 
                 arg2: Optional[str] = None, result: Optional[str] = None):
        self.operator = operator
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result
    
    def __repr__(self):
        return f"({self.operator}, {self.arg1 or '-'}, {self.arg2 or '-'}, {self.result or '-'})"
    
    def to_string(self) -> str:
        """Convert quadruple to readable string format"""
        op = self.operator
        a1 = self.arg1 if self.arg1 is not None else "-"
        a2 = self.arg2 if self.arg2 is not None else "-"
        res = self.result if self.result is not None else "-"
        
        # Format based on operator type
        if op == "label":
            return f"{a1}:"
        elif op == "goto":
            return f"goto {res}"
        elif op == "ifFalse":
            return f"ifFalse {a1} goto {res}"
        elif op == "if":
            return f"if {a1} goto {res}"
        elif op == "=":
            return f"{res} = {a1}"
        elif op in ["+", "-", "*", "/", "%", "==", "!=", ">", "<", ">=", "<=", "and", "or"]:
            return f"{res} = {a1} {op} {a2}"
        elif op == "unary-":
            return f"{res} = -{a1}"
        elif op == "not":
            return f"{res} = not {a1}"
        elif op == "[]":
            return f"{res} = {a1}[{a2}]"
        elif op == "[]=":
            return f"{a1}[{a2}] = {res}"
        elif op == ".":
            return f"{res} = {a1}.{a2}"
        elif op == ".=":
            return f"{a1}.{a2} = {res}"
        elif op == "call":
            if res:
                return f"{res} = call {a1}, {a2}"
            return f"call {a1}, {a2}"
        elif op == "param":
            return f"param {a1}"
        elif op == "return":
            if a1:
                return f"return {a1}"
            return "return"
        elif op == "begin_func":
            return f"begin_func {a1}"
        elif op == "end_func":
            return f"end_func {a1}"
        elif op == "allocate":
            return f"{res} = allocate {a1} {a2}"
        elif op == "cast":
            return f"{res} = ({a1}) {a2}"
        elif op == "nop":
            return "nop"
        elif op == "comment":
            return f"# {a1}"
        else:
            return f"({op}, {a1}, {a2}, {res})"


class QuadrupleTable:
    """Container for quadruples with index tracking"""
    
    def __init__(self):
        self.quadruples: List[Quadruple] = []
        self.next_index = 0
    
    def emit(self, operator: str, arg1: Optional[str] = None,
             arg2: Optional[str] = None, result: Optional[str] = None) -> int:
        """Emit a new quadruple and return its index"""
        quad = Quadruple(operator, arg1, arg2, result)
        self.quadruples.append(quad)
        index = self.next_index
        self.next_index += 1
        return index
    
    def get(self, index: int) -> Quadruple:
        """Get quadruple at index"""
        return self.quadruples[index]
    
    def backpatch(self, index: int, label: str):
        """Backpatch a quadruple's result field with a label"""
        if 0 <= index < len(self.quadruples):
            self.quadruples[index].result = label
    
    def __len__(self):
        return len(self.quadruples)
    
    def __iter__(self):
        return iter(self.quadruples)
    
    def __repr__(self):
        return f"QuadrupleTable({len(self.quadruples)} quads)"
    
    def to_string(self, with_index: bool = True) -> str:
        """Convert all quadruples to string representation"""
        lines = []
        for i, quad in enumerate(self.quadruples):
            if with_index:
                lines.append(f"{i:4d}: {quad.to_string()}")
            else:
                lines.append(quad.to_string())
        return "\n".join(lines)


def create_binary_quad(operator: str, arg1: str, arg2: str, result: str) -> Quadruple:
    """Helper to create binary operation quadruple"""
    return Quadruple(operator, arg1, arg2, result)


def create_unary_quad(operator: str, arg: str, result: str) -> Quadruple:
    """Helper to create unary operation quadruple"""
    if operator == "-":
        operator = "unary-"
    return Quadruple(operator, arg, None, result)


def create_assign_quad(source: str, dest: str) -> Quadruple:
    """Helper to create assignment quadruple"""
    return Quadruple("=", source, None, dest)


def create_goto_quad(label: str) -> Quadruple:
    """Helper to create unconditional goto quadruple"""
    return Quadruple("goto", None, None, label)


def create_if_quad(condition: str, label: str, negated: bool = False) -> Quadruple:
    """Helper to create conditional goto quadruple"""
    op = "ifFalse" if negated else "if"
    return Quadruple(op, condition, None, label)


def create_label_quad(label: str) -> Quadruple:
    """Helper to create label quadruple"""
    return Quadruple("label", label, None, None)


def create_param_quad(arg: str) -> Quadruple:
    """Helper to create parameter quadruple"""
    return Quadruple("param", arg, None, None)


def create_call_quad(func_name: str, num_params: int, result: Optional[str] = None) -> Quadruple:
    """Helper to create function call quadruple"""
    return Quadruple("call", func_name, str(num_params), result)


def create_return_quad(value: Optional[str] = None) -> Quadruple:
    """Helper to create return quadruple"""
    return Quadruple("return", value, None, None)


def create_array_read_quad(array: str, index: str, result: str) -> Quadruple:
    """Helper to create array read quadruple"""
    return Quadruple("[]", array, index, result)


def create_array_write_quad(array: str, index: str, value: str) -> Quadruple:
    """Helper to create array write quadruple"""
    return Quadruple("[]=", array, index, value)


def create_table_read_quad(table: str, field: str, result: str) -> Quadruple:
    """Helper to create table read quadruple"""
    return Quadruple(".", table, field, result)


def create_table_write_quad(table: str, field: str, value: str) -> Quadruple:
    """Helper to create table write quadruple"""
    return Quadruple(".=", table, field, value)
