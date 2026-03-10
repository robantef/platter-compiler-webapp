"""
Algebraic Simplification Optimization Pass

Applies algebraic identities to simplify expressions.

Examples:
    x + 0 => x
    x * 1 => x
    x * 0 => 0
    x - 0 => x
    x / 1 => x
    x - x => 0
    x / x => 1
    0 - x => -x
"""

from typing import List
from .optimizer import OptimizationPass
from .tac import *
from .quadruple import *


class AlgebraicSimplificationPass(OptimizationPass):
    """Simplifies expressions using algebraic identities"""
    
    def __init__(self):
        super().__init__("Algebraic Simplification")
    
    def optimize_tac(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Apply algebraic simplifications to TAC"""
        self.reset_stats()
        optimized = []
        
        for instr in instructions:
            simplified = self._simplify_tac(instr)
            optimized.append(simplified)
        
        return optimized
    
    def optimize_quads(self, quad_table: QuadrupleTable) -> QuadrupleTable:
        """Apply algebraic simplifications to quadruples"""
        self.reset_stats()
        new_table = QuadrupleTable()
        
        for quad in quad_table.quadruples:
            simplified = self._simplify_quad(quad)
            new_table.quadruples.append(simplified)
        
        return new_table
    
    def _simplify_tac(self, instr: TACInstruction) -> TACInstruction:
        """Simplify a single TAC instruction"""
        if not isinstance(instr, TACBinaryOp):
            return instr
        
        op = instr.operator
        arg1 = instr.arg1
        arg2 = instr.arg2
        result = instr.result
        
        # Addition identities
        if op == '+':
            if self._is_zero(arg2):  # x + 0 => x
                self.changes_made += 1
                return TACAssignment(result, arg1)
            if self._is_zero(arg1):  # 0 + x => x
                self.changes_made += 1
                return TACAssignment(result, arg2)
        
        # Subtraction identities
        elif op == '-':
            if self._is_zero(arg2):  # x - 0 => x
                self.changes_made += 1
                return TACAssignment(result, arg1)
            if arg1 == arg2:  # x - x => 0
                self.changes_made += 1
                return TACAssignment(result, '0')
            if self._is_zero(arg1):  # 0 - x => -x
                self.changes_made += 1
                return TACUnaryOp(result, '-', arg2)
        
        # Multiplication identities
        elif op == '*':
            if self._is_one(arg2):  # x * 1 => x
                self.changes_made += 1
                return TACAssignment(result, arg1)
            if self._is_one(arg1):  # 1 * x => x
                self.changes_made += 1
                return TACAssignment(result, arg2)
            if self._is_zero(arg2) or self._is_zero(arg1):  # x * 0 => 0
                self.changes_made += 1
                return TACAssignment(result, '0')
            # Power of 2 multiplication could be converted to shift
            if self._is_power_of_2(arg2):
                # t = x * 2 => t = x + x (could be further optimized to shift)
                pass
        
        # Division identities
        elif op == '/':
            if self._is_one(arg2):  # x / 1 => x
                self.changes_made += 1
                return TACAssignment(result, arg1)
            if arg1 == arg2:  # x / x => 1 (assuming x != 0)
                self.changes_made += 1
                return TACAssignment(result, '1')
            if self._is_zero(arg1):  # 0 / x => 0 (assuming x != 0)
                self.changes_made += 1
                return TACAssignment(result, '0')
        
        # Modulo identities
        elif op == '%':
            if self._is_one(arg2):  # x % 1 => 0
                self.changes_made += 1
                return TACAssignment(result, '0')
            if arg1 == arg2:  # x % x => 0 (assuming x != 0)
                self.changes_made += 1
                return TACAssignment(result, '0')
        
        # Boolean identities
        elif op == 'and':
            if self._is_true(arg1):  # true and x => x
                self.changes_made += 1
                return TACAssignment(result, arg2)
            if self._is_true(arg2):  # x and true => x
                self.changes_made += 1
                return TACAssignment(result, arg1)
            if self._is_false(arg1) or self._is_false(arg2):  # x and false => false
                self.changes_made += 1
                return TACAssignment(result, 'false')
        
        elif op == 'or':
            if self._is_false(arg1):  # false or x => x
                self.changes_made += 1
                return TACAssignment(result, arg2)
            if self._is_false(arg2):  # x or false => x
                self.changes_made += 1
                return TACAssignment(result, arg1)
            if self._is_true(arg1) or self._is_true(arg2):  # x or true => true
                self.changes_made += 1
                return TACAssignment(result, 'true')
        
        return instr
    
    def _simplify_quad(self, quad: Quadruple) -> Quadruple:
        """Simplify a single quadruple"""
        op = quad.operator
        arg1 = quad.arg1
        arg2 = quad.arg2
        result = quad.result
        
        # Addition
        if op == '+':
            if self._is_zero(arg2):
                self.changes_made += 1
                return Quadruple('=', arg1, None, result)
            if self._is_zero(arg1):
                self.changes_made += 1
                return Quadruple('=', arg2, None, result)
        
        # Subtraction
        elif op == '-':
            if self._is_zero(arg2):
                self.changes_made += 1
                return Quadruple('=', arg1, None, result)
            if arg1 == arg2:
                self.changes_made += 1
                return Quadruple('=', '0', None, result)
            if self._is_zero(arg1):
                self.changes_made += 1
                return Quadruple('unary-', arg2, None, result)
        
        # Multiplication
        elif op == '*':
            if self._is_one(arg2):
                self.changes_made += 1
                return Quadruple('=', arg1, None, result)
            if self._is_one(arg1):
                self.changes_made += 1
                return Quadruple('=', arg2, None, result)
            if self._is_zero(arg2) or self._is_zero(arg1):
                self.changes_made += 1
                return Quadruple('=', '0', None, result)
        
        # Division
        elif op == '/':
            if self._is_one(arg2):
                self.changes_made += 1
                return Quadruple('=', arg1, None, result)
            if arg1 == arg2:
                self.changes_made += 1
                return Quadruple('=', '1', None, result)
            if self._is_zero(arg1):
                self.changes_made += 1
                return Quadruple('=', '0', None, result)
        
        # Modulo
        elif op == '%':
            if self._is_one(arg2):
                self.changes_made += 1
                return Quadruple('=', '0', None, result)
            if arg1 == arg2:
                self.changes_made += 1
                return Quadruple('=', '0', None, result)
        
        # Boolean
        elif op == 'and':
            if self._is_true(arg1):
                self.changes_made += 1
                return Quadruple('=', arg2, None, result)
            if self._is_true(arg2):
                self.changes_made += 1
                return Quadruple('=', arg1, None, result)
            if self._is_false(arg1) or self._is_false(arg2):
                self.changes_made += 1
                return Quadruple('=', 'false', None, result)
        
        elif op == 'or':
            if self._is_false(arg1):
                self.changes_made += 1
                return Quadruple('=', arg2, None, result)
            if self._is_false(arg2):
                self.changes_made += 1
                return Quadruple('=', arg1, None, result)
            if self._is_true(arg1) or self._is_true(arg2):
                self.changes_made += 1
                return Quadruple('=', 'true', None, result)
        
        return quad
    
    def _is_zero(self, value: str) -> bool:
        """Check if value is zero"""
        return value in ('0', '0.0')
    
    def _is_one(self, value: str) -> bool:
        """Check if value is one"""
        return value in ('1', '1.0')
    
    def _is_true(self, value: str) -> bool:
        """Check if value is true"""
        return value in ('true', 'True')
    
    def _is_false(self, value: str) -> bool:
        """Check if value is false"""
        return value in ('false', 'False')
    
    def _is_power_of_2(self, value: str) -> bool:
        """Check if value is a power of 2"""
        try:
            n = int(value)
            return n > 0 and (n & (n - 1)) == 0
        except ValueError:
            return False


class StrengthReductionPass(OptimizationPass):
    """Replaces expensive operations with cheaper equivalents"""
    
    def __init__(self):
        super().__init__("Strength Reduction")
    
    def optimize_tac(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Apply strength reduction to TAC"""
        self.reset_stats()
        optimized = []
        
        for instr in instructions:
            reduced = self._reduce_tac(instr)
            optimized.append(reduced)
        
        return optimized
    
    def optimize_quads(self, quad_table: QuadrupleTable) -> QuadrupleTable:
        """Apply strength reduction to quadruples"""
        self.reset_stats()
        new_table = QuadrupleTable()
        
        for quad in quad_table.quadruples:
            reduced = self._reduce_quad(quad)
            new_table.quadruples.append(reduced)
        
        return new_table
    
    def _reduce_tac(self, instr: TACInstruction) -> TACInstruction:
        """Reduce expensive operations"""
        if not isinstance(instr, TACBinaryOp):
            return instr
        
        # Multiplication by power of 2 => left shift
        # Division by power of 2 => right shift
        # x * 2 => x + x
        # x ** 2 => x * x
        
        if instr.operator == '*':
            if instr.arg2 == '2':
                # x * 2 => x + x
                self.changes_made += 1
                return TACBinaryOp(instr.result, '+', instr.arg1, instr.arg1)
        
        return instr
    
    def _reduce_quad(self, quad: Quadruple) -> Quadruple:
        """Reduce expensive operations in quadruples"""
        if quad.operator == '*' and quad.arg2 == '2':
            self.changes_made += 1
            return Quadruple('+', quad.arg1, quad.arg1, quad.result)
        
        return quad
