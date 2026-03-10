"""
Dead Code Elimination Optimization Pass

Removes instructions that compute values that are never used.
Also removes unreachable code after unconditional jumps and returns.

Examples:
    t1 = 5        (dead if t1 never used)
    t2 = x + 3    (dead if t2 never used)
    
    return x
    y = 5         (unreachable)
"""

from typing import List, Set, Dict
from .optimizer import OptimizationPass, ControlFlowGraph
from .tac import *
from .quadruple import *


class DeadCodeEliminationPass(OptimizationPass):
    """Eliminates dead code and unreachable code"""
    
    def __init__(self):
        super().__init__("Dead Code Elimination")
        self.live_vars: Set[str] = set()
        self.used_vars: Set[str] = set()
    
    def optimize_tac(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Eliminate dead code in TAC"""
        self.reset_stats()
        
        # First pass: remove unreachable code
        reachable = self._remove_unreachable_tac(instructions)
        
        # Second pass: remove unused assignments
        optimized = self._remove_dead_assignments_tac(reachable)
        
        return optimized
    
    def optimize_quads(self, quad_table: QuadrupleTable) -> QuadrupleTable:
        """Eliminate dead code in quadruples"""
        self.reset_stats()
        
        # Convert to list for processing
        quads_list = list(quad_table.quadruples)
        
        # Remove unreachable code
        reachable = self._remove_unreachable_quads(quads_list)
        
        # Remove dead assignments
        optimized = self._remove_dead_assignments_quads(reachable)
        
        # Build new table
        new_table = QuadrupleTable()
        for quad in optimized:
            new_table.emit(quad.operator, quad.arg1, quad.arg2, quad.result)
        
        return new_table
    
    def _remove_unreachable_tac(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Remove code after returns and unconditional jumps"""
        reachable = []
        skip_until_label = False
        
        for instr in instructions:
            if skip_until_label:
                # Skip until we hit a new control-flow boundary
                # Keep function boundaries intact (FUNC_END is required by interpreter)
                if isinstance(instr, (TACLabel, TACFunctionBegin, TACFunctionEnd)):
                    skip_until_label = False
                    reachable.append(instr)
                else:
                    self.changes_made += 1
                    continue
            else:
                reachable.append(instr)
                
                # After return or unconditional goto, code is unreachable
                if isinstance(instr, (TACReturn, TACGoto)):
                    skip_until_label = True
        
        return reachable
    
    def _remove_dead_assignments_tac(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Remove assignments to variables that are never used"""
        # Backward pass: collect all used variables
        self.used_vars = set()
        
        for instr in reversed(instructions):
            self._collect_used_vars_tac(instr)
        
        # Forward pass: remove dead assignments
        optimized = []
        for instr in instructions:
            if self._is_dead_assignment_tac(instr):
                self.changes_made += 1
                continue
            optimized.append(instr)
        
        return optimized
    
    def _collect_used_vars_tac(self, instr: TACInstruction):
        """Collect variables that are used"""
        if isinstance(instr, TACBinaryOp):
            self._add_if_var(instr.arg1)
            self._add_if_var(instr.arg2)
        elif isinstance(instr, TACUnaryOp):
            self._add_if_var(instr.arg1)
        elif isinstance(instr, TACAssignment):
            self._add_if_var(instr.arg1)
        elif isinstance(instr, TACArrayAccess):
            self._add_if_var(instr.array)
            self._add_if_var(instr.index)
        elif isinstance(instr, TACArrayAssign):
            self._add_if_var(instr.array)
            self._add_if_var(instr.index)
            self._add_if_var(instr.value)
        elif isinstance(instr, TACTableAccess):
            self._add_if_var(instr.table)
        elif isinstance(instr, TACTableAssign):
            self._add_if_var(instr.table)
            self._add_if_var(instr.value)
        elif isinstance(instr, TACConditionalGoto):
            self._add_if_var(instr.condition)
        elif isinstance(instr, TACReturn):
            if instr.value:
                self._add_if_var(instr.value)
        elif isinstance(instr, TACParam):
            self._add_if_var(instr.arg)
    
    def _is_dead_assignment_tac(self, instr: TACInstruction) -> bool:
        """Check if an assignment is dead"""
        # Only remove simple assignments and computations to temporaries
        if isinstance(instr, (TACAssignment, TACBinaryOp, TACUnaryOp, TACCast)):
            result = instr.result
            # Check if result is never used
            if result.startswith('t') and result not in self.used_vars:
                return True
        
        return False
    
    def _remove_unreachable_quads(self, quads: List[Quadruple]) -> List[Quadruple]:
        """Remove unreachable quadruples"""
        reachable = []
        skip_until_label = False
        
        for quad in quads:
            if skip_until_label:
                if quad.operator in ['label', 'begin_func', 'end_func']:
                    skip_until_label = False
                    reachable.append(quad)
                else:
                    self.changes_made += 1
                    continue
            else:
                reachable.append(quad)
                
                if quad.operator in ['return', 'goto']:
                    skip_until_label = True
        
        return reachable
    
    def _remove_dead_assignments_quads(self, quads: List[Quadruple]) -> List[Quadruple]:
        """Remove dead assignments in quadruples"""
        # Collect used variables
        self.used_vars = set()
        for quad in reversed(quads):
            self._collect_used_vars_quad(quad)
        
        # Remove dead assignments
        optimized = []
        for quad in quads:
            if self._is_dead_assignment_quad(quad):
                self.changes_made += 1
                continue
            optimized.append(quad)
        
        return optimized
    
    def _collect_used_vars_quad(self, quad: Quadruple):
        """Collect used variables from quadruple"""
        if quad.arg1:
            self._add_if_var(quad.arg1)
        if quad.arg2:
            self._add_if_var(quad.arg2)
        # Result in some cases is also used (e.g., goto targets)
        if quad.operator in ['goto', 'if', 'ifFalse'] and quad.result:
            self._add_if_var(quad.result)
    
    def _is_dead_assignment_quad(self, quad: Quadruple) -> bool:
        """Check if quadruple is dead assignment"""
        if quad.operator == '=' or quad.operator in ['+', '-', '*', '/', '%', 
                                                       '==', '!=', '>', '<', '>=', '<=',
                                                       'unary-', 'not', 'cast']:
            result = quad.result
            if result and result.startswith('t') and result not in self.used_vars:
                return True
        
        return False
    
    def _add_if_var(self, value: str):
        """Add value to used_vars if it's a variable"""
        if value and self._is_variable(value):
            self.used_vars.add(value)
    
    def _is_variable(self, value: str) -> bool:
        """Check if value is a variable"""
        if not value:
            return False
        try:
            float(value)
            return False
        except ValueError:
            return value not in ('true', 'false', 'True', 'False')


class UnreachableCodeEliminationPass(OptimizationPass):
    """Eliminates unreachable code using CFG analysis"""
    
    def __init__(self):
        super().__init__("Unreachable Code Elimination")
    
    def optimize_tac(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Remove unreachable code using control flow analysis"""
        self.reset_stats()
        
        # Build CFG
        cfg = ControlFlowGraph()
        cfg.build_from_tac(instructions)
        
        # Find reachable blocks
        reachable_blocks = self._find_reachable_blocks(cfg)
        
        # Collect instructions from reachable blocks
        optimized = []
        for block in cfg.blocks:
            if block.id in reachable_blocks:
                optimized.extend(block.instructions)
            else:
                self.changes_made += len(block.instructions)
        
        return optimized
    
    def optimize_quads(self, quad_table: QuadrupleTable) -> QuadrupleTable:
        """Remove unreachable code (simplified for quadruples)"""
        # Use simpler approach for quadruples
        return quad_table
    
    def _find_reachable_blocks(self, cfg: ControlFlowGraph) -> Set[int]:
        """Find all reachable blocks from entry using DFS"""
        reachable = set()
        stack = [0]  # Start from entry block
        
        while stack:
            block_id = stack.pop()
            if block_id in reachable:
                continue
            
            reachable.add(block_id)
            block = cfg.get_block(block_id)
            
            if block:
                for succ_id in block.successors:
                    if succ_id not in reachable:
                        stack.append(succ_id)
        
        return reachable
