"""
Constant Propagation and Copy Propagation Optimization Passes

Constant Propagation: Replaces uses of variables that have constant values
    x = 5
    y = x + 3   ->   y = 5 + 3

Copy Propagation: Replaces uses of variables that are copies of other variables
    x = y
    z = x + 1   ->   z = y + 1
"""

from typing import List, Dict, Optional, Set
from .optimizer import OptimizationPass
from .tac import *
from .quadruple import *


class ConstantPropagationPass(OptimizationPass):
    """Propagates constant values through the code"""
    
    def __init__(self):
        super().__init__("Constant Propagation")
        self.constants: Dict[str, str] = {}
    
    def optimize_tac(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Propagate constants in TAC"""
        self.reset_stats()
        self.constants = {}
        optimized = []
        
        for instr in instructions:
            # Track constant assignments
            if isinstance(instr, TACAssignment):
                if self._is_constant(instr.arg1):
                    self.constants[instr.result] = instr.arg1
                elif instr.arg1 in self.constants:
                    # Propagate constant
                    self.constants[instr.result] = self.constants[instr.arg1]
                else:
                    # Remove from constants if reassigned
                    if instr.result in self.constants:
                        del self.constants[instr.result]
                optimized.append(instr)
            
            elif isinstance(instr, TACBinaryOp):
                # Replace operands with constants if available
                new_instr = self._propagate_binary_tac(instr)
                optimized.append(new_instr)
                
                # Remove result from constants (it's computed)
                if instr.result in self.constants:
                    del self.constants[instr.result]
            
            elif isinstance(instr, TACUnaryOp):
                new_instr = self._propagate_unary_tac(instr)
                optimized.append(new_instr)
                
                if instr.result in self.constants:
                    del self.constants[instr.result]
            
            elif isinstance(instr, TACConditionalGoto):
                new_instr = self._propagate_condition_tac(instr)
                optimized.append(new_instr)
            
            elif isinstance(instr, (TACFunctionCall, TACLabel, TACGoto)):
                # Clear constants at function calls and labels (conservative)
                if isinstance(instr, (TACFunctionCall, TACLabel)):
                    self.constants = {}
                optimized.append(instr)
            
            else:
                optimized.append(instr)
        
        return optimized
    
    def optimize_quads(self, quad_table: QuadrupleTable) -> QuadrupleTable:
        """Propagate constants in quadruples"""
        self.reset_stats()
        self.constants = {}
        new_table = QuadrupleTable()
        
        for quad in quad_table.quadruples:
            if quad.operator == '=':
                if self._is_constant(quad.arg1):
                    self.constants[quad.result] = quad.arg1
                elif quad.arg1 in self.constants:
                    self.constants[quad.result] = self.constants[quad.arg1]
                else:
                    if quad.result in self.constants:
                        del self.constants[quad.result]
                new_table.emit(quad.operator, quad.arg1, quad.arg2, quad.result)
            
            elif quad.operator in ['+', '-', '*', '/', '%', '==', '!=  ', '>', '<', '>=', '<=', 'and', 'or']:
                new_quad = self._propagate_binary_quad(quad)
                new_table.emit(new_quad.operator, new_quad.arg1, new_quad.arg2, new_quad.result)
                
                if quad.result in self.constants:
                    del self.constants[quad.result]
            
            elif quad.operator in ['label', 'call']:
                self.constants = {}
                new_table.emit(quad.operator, quad.arg1, quad.arg2, quad.result)
            
            else:
                new_table.emit(quad.operator, quad.arg1, quad.arg2, quad.result)
        
        return new_table
    
    def _propagate_binary_tac(self, instr: TACBinaryOp) -> TACBinaryOp:
        """Propagate constants in binary operation"""
        arg1 = self.constants.get(instr.arg1, instr.arg1)
        arg2 = self.constants.get(instr.arg2, instr.arg2)
        
        if arg1 != instr.arg1 or arg2 != instr.arg2:
            self.changes_made += 1
            return TACBinaryOp(instr.result, arg1, instr.operator, arg2)
        
        return instr
    
    def _propagate_unary_tac(self, instr: TACUnaryOp) -> TACUnaryOp:
        """Propagate constants in unary operation"""
        arg1 = self.constants.get(instr.arg1, instr.arg1)
        
        if arg1 != instr.arg1:
            self.changes_made += 1
            return TACUnaryOp(instr.result, instr.operator, arg1)
        
        return instr
    
    def _propagate_condition_tac(self, instr: TACConditionalGoto) -> TACConditionalGoto:
        """Propagate constants in conditional"""
        condition = self.constants.get(instr.condition, instr.condition)
        
        if condition != instr.condition:
            self.changes_made += 1
            return TACConditionalGoto(condition, instr.label, instr.negated)
        
        return instr
    
    def _propagate_binary_quad(self, quad: Quadruple) -> Quadruple:
        """Propagate constants in binary quadruple"""
        arg1 = self.constants.get(quad.arg1, quad.arg1)
        arg2 = self.constants.get(quad.arg2, quad.arg2)
        
        if arg1 != quad.arg1 or arg2 != quad.arg2:
            self.changes_made += 1
        
        return Quadruple(quad.operator, arg1, arg2, quad.result)
    
    def _is_constant(self, value: str) -> bool:
        """Check if a value is a constant literal"""
        if not value:
            return False
        try:
            float(value)
            return True
        except ValueError:
            return value in ('true', 'false', 'True', 'False')


class CopyPropagationPass(OptimizationPass):
    """Propagates copy assignments (x = y)"""
    
    def __init__(self):
        super().__init__("Copy Propagation")
        self.copies: Dict[str, str] = {}
    
    def optimize_tac(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Propagate copies in TAC"""
        self.reset_stats()
        self.copies = {}
        optimized = []
        
        for instr in instructions:
            if isinstance(instr, TACAssignment):
                # Check if this is a copy (x = y where y is a variable)
                if self._is_variable(instr.arg1):
                    self.copies[instr.result] = instr.arg1
                else:
                    # Remove from copies if reassigned
                    if instr.result in self.copies:
                        del self.copies[instr.result]
                optimized.append(instr)
            
            elif isinstance(instr, TACBinaryOp):
                new_instr = self._propagate_copy_binary_tac(instr)
                optimized.append(new_instr)
                
                if instr.result in self.copies:
                    del self.copies[instr.result]
            
            elif isinstance(instr, TACUnaryOp):
                new_instr = self._propagate_copy_unary_tac(instr)
                optimized.append(new_instr)
                
                if instr.result in self.copies:
                    del self.copies[instr.result]
            
            elif isinstance(instr, (TACFunctionCall, TACLabel)):
                # Clear copies at function calls and labels
                self.copies = {}
                optimized.append(instr)
            
            else:
                optimized.append(instr)
        
        return optimized
    
    def optimize_quads(self, quad_table: QuadrupleTable) -> QuadrupleTable:
        """Propagate copies in quadruples"""
        self.reset_stats()
        self.copies = {}
        new_table = QuadrupleTable()
        
        for quad in quad_table.quadruples:
            if quad.operator == '=' and self._is_variable(quad.arg1):
                self.copies[quad.result] = quad.arg1
                new_table.emit(quad.operator, quad.arg1, quad.arg2, quad.result)
            
            elif quad.operator in ['+', '-', '*', '/', '%', '==', '!=', '>', '<', '>=', '<=']:
                new_quad = self._propagate_copy_binary_quad(quad)
                new_table.emit(new_quad.operator, new_quad.arg1, new_quad.arg2, new_quad.result)
                
                if quad.result in self.copies:
                    del self.copies[quad.result]
            
            elif quad.operator in ['label', 'call']:
                self.copies = {}
                new_table.emit(quad.operator, quad.arg1, quad.arg2, quad.result)
            
            else:
                new_table.emit(quad.operator, quad.arg1, quad.arg2, quad.result)
        
        return new_table
    
    def _propagate_copy_binary_tac(self, instr: TACBinaryOp) -> TACBinaryOp:
        """Propagate copies in binary operation"""
        arg1 = self.copies.get(instr.arg1, instr.arg1)
        arg2 = self.copies.get(instr.arg2, instr.arg2)
        
        if arg1 != instr.arg1 or arg2 != instr.arg2:
            self.changes_made += 1
            return TACBinaryOp(instr.result, arg1, instr.operator, arg2)
        
        return instr
    
    def _propagate_copy_unary_tac(self, instr: TACUnaryOp) -> TACUnaryOp:
        """Propagate copies in unary operation"""
        arg1 = self.copies.get(instr.arg1, instr.arg1)
        
        if arg1 != instr.arg1:
            self.changes_made += 1
            return TACUnaryOp(instr.result, instr.operator, arg1)
        
        return instr
    
    def _propagate_copy_binary_quad(self, quad: Quadruple) -> Quadruple:
        """Propagate copies in binary quadruple"""
        arg1 = self.copies.get(quad.arg1, quad.arg1)
        arg2 = self.copies.get(quad.arg2, quad.arg2) if quad.arg2 else None
        
        if arg1 != quad.arg1 or (quad.arg2 and arg2 != quad.arg2):
            self.changes_made += 1
        
        return Quadruple(quad.operator, arg1, arg2, quad.result)
    
    def _is_variable(self, value: str) -> bool:
        """Check if value is a variable (not a constant)"""
        if not value:
            return False
        try:
            float(value)
            return False
        except ValueError:
            return value not in ('true', 'false', 'True', 'False')
