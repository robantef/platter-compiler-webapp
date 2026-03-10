"""
Constant Folding Optimization Pass

This optimization evaluates constant expressions at compile time.
Examples:
    t1 = 2 + 3    ->   t1 = 5
    t2 = 10 * 5   ->   t2 = 50
    t3 = 7 > 3    ->   t3 = true
"""

from typing import List, Optional, Union
from .optimizer import OptimizationPass
from .tac import *
from .quadruple import *


class ConstantFoldingPass(OptimizationPass):
    """Performs constant folding on TAC and Quadruples"""
    
    def __init__(self):
        super().__init__("Constant Folding")
    
    def optimize_tac(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Optimize TAC instructions by folding constants"""
        self.reset_stats()
        optimized = []
        
        for instr in instructions:
            if isinstance(instr, TACBinaryOp):
                folded = self._fold_binary_op_tac(instr)
                if folded:
                    optimized.append(folded)
                    self.changes_made += 1
                else:
                    optimized.append(instr)
            elif isinstance(instr, TACUnaryOp):
                folded = self._fold_unary_op_tac(instr)
                if folded:
                    optimized.append(folded)
                    self.changes_made += 1
                else:
                    optimized.append(instr)
            else:
                optimized.append(instr)
        
        return optimized
    
    def optimize_quads(self, quad_table: QuadrupleTable) -> QuadrupleTable:
        """Optimize quadruples by folding constants"""
        self.reset_stats()
        new_table = QuadrupleTable()
        
        for quad in quad_table.quadruples:
            if quad.operator in ['+', '-', '*', '/', '%', '==', '!=', '>', '<', '>=', '<=', 'and', 'or']:
                folded = self._fold_binary_op_quad(quad)
                if folded:
                    new_table.emit(folded.operator, folded.arg1, folded.arg2, folded.result)
                    self.changes_made += 1
                else:
                    new_table.emit(quad.operator, quad.arg1, quad.arg2, quad.result)
            elif quad.operator in ['unary-', 'not']:
                folded = self._fold_unary_op_quad(quad)
                if folded:
                    new_table.emit(folded.operator, folded.arg1, folded.arg2, folded.result)
                    self.changes_made += 1
                else:
                    new_table.emit(quad.operator, quad.arg1, quad.arg2, quad.result)
            else:
                new_table.emit(quad.operator, quad.arg1, quad.arg2, quad.result)
        
        return new_table
    
    def _fold_binary_op_tac(self, instr: TACBinaryOp) -> Optional[TACAssignment]:
        """Try to fold a binary operation"""
        val1 = self._parse_literal(instr.arg1)
        val2 = self._parse_literal(instr.arg2)
        
        if val1 is None or val2 is None:
            return None
        
        result = self._evaluate_binary(val1, instr.operator, val2)
        if result is not None:
            return TACAssignment(instr.result, str(result))
        
        return None
    
    def _fold_unary_op_tac(self, instr: TACUnaryOp) -> Optional[TACAssignment]:
        """Try to fold a unary operation"""
        val = self._parse_literal(instr.arg1)
        
        if val is None:
            return None
        
        result = self._evaluate_unary(instr.operator, val)
        if result is not None:
            return TACAssignment(instr.result, str(result))
        
        return None
    
    def _fold_binary_op_quad(self, quad: Quadruple) -> Optional[Quadruple]:
        """Try to fold a binary operation quadruple"""
        val1 = self._parse_literal(quad.arg1)
        val2 = self._parse_literal(quad.arg2)
        
        if val1 is None or val2 is None:
            return None
        
        result = self._evaluate_binary(val1, quad.operator, val2)
        if result is not None:
            return Quadruple('=', str(result), None, quad.result)
        
        return None
    
    def _fold_unary_op_quad(self, quad: Quadruple) -> Optional[Quadruple]:
        """Try to fold a unary operation quadruple"""
        val = self._parse_literal(quad.arg1)
        
        if val is None:
            return None
        
        result = self._evaluate_unary(quad.operator, val)
        if result is not None:
            return Quadruple('=', str(result), None, quad.result)
        
        return None
    
    def _parse_literal(self, value: str) -> Optional[Union[int, float, bool]]:
        """Parse a literal value from string"""
        if value is None:
            return None
        
        # Try boolean
        if value in ('true', 'True', '1'):
            return True
        if value in ('false', 'False', '0'):
            return False
        
        # Try int
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        return None
    
    def _evaluate_binary(self, left: Union[int, float, bool], 
                        op: str, 
                        right: Union[int, float, bool]) -> Optional[Union[int, float, bool]]:
        """Evaluate binary operation"""
        try:
            if op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                if right == 0:
                    return None  # Don't fold division by zero
                # Integer division for ints, float division for floats
                if isinstance(left, int) and isinstance(right, int):
                    return left // right
                return left / right
            elif op == '%':
                if right == 0:
                    return None
                return left % right
            elif op == '==':
                return left == right
            elif op == '!=':
                return left != right
            elif op == '>':
                return left > right
            elif op == '<':
                return left < right
            elif op == '>=':
                return left >= right
            elif op == '<=':
                return left <= right
            elif op == 'and':
                return bool(left) and bool(right)
            elif op == 'or':
                return bool(left) or bool(right)
        except (TypeError, ZeroDivisionError, ValueError):
            return None
        
        return None
    
    def _evaluate_unary(self, op: str, value: Union[int, float, bool]) -> Optional[Union[int, float, bool]]:
        """Evaluate unary operation"""
        try:
            if op in ('-', 'unary-'):
                return -value
            elif op == 'not':
                return not bool(value)
        except (TypeError, ValueError):
            return None
        
        return None
