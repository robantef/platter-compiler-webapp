"""
Base Optimizer Classes for Intermediate Code Optimization

This module provides the base classes and infrastructure for implementing
various optimization passes on TAC and Quadruple representations.
"""

from typing import List, Set, Dict, Optional, Any
from abc import ABC, abstractmethod
from .tac import *
from .quadruple import *


class OptimizationPass(ABC):
    """Base class for all optimization passes"""
    
    def __init__(self, name: str):
        self.name = name
        self.changes_made = 0
        self.enabled = True
    
    @abstractmethod
    def optimize_tac(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """
        Optimize TAC instructions.
        Returns optimized instruction list.
        """
        pass
    
    @abstractmethod
    def optimize_quads(self, quad_table: QuadrupleTable) -> QuadrupleTable:
        """
        Optimize quadruples.
        Returns optimized quadruple table.
        """
        pass
    
    def reset_stats(self):
        """Reset optimization statistics"""
        self.changes_made = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        return {
            "name": self.name,
            "changes_made": self.changes_made,
            "enabled": self.enabled
        }


class BasicBlock:
    """Represents a basic block in control flow graph"""
    
    def __init__(self, block_id: int):
        self.id = block_id
        self.instructions: List[TACInstruction] = []
        self.quadruples: List[Quadruple] = []
        self.predecessors: Set[int] = set()
        self.successors: Set[int] = set()
        self.start_index = 0
        self.end_index = 0
        
        # Data flow analysis
        self.use: Set[str] = set()  # Variables used before definition
        self.def_vars: Set[str] = set()  # Variables defined
        self.live_in: Set[str] = set()  # Live variables at entry
        self.live_out: Set[str] = set()  # Live variables at exit
    
    def add_instruction(self, instr: TACInstruction):
        """Add TAC instruction to block"""
        self.instructions.append(instr)
    
    def add_quadruple(self, quad: Quadruple):
        """Add quadruple to block"""
        self.quadruples.append(quad)
    
    def add_successor(self, block_id: int):
        """Add successor block"""
        self.successors.add(block_id)
    
    def add_predecessor(self, block_id: int):
        """Add predecessor block"""
        self.predecessors.add(block_id)
    
    def __repr__(self):
        return f"Block{self.id}(instrs={len(self.instructions)}, preds={self.predecessors}, succs={self.successors})"


class ControlFlowGraph:
    """Control Flow Graph for data flow analysis"""
    
    def __init__(self):
        self.blocks: List[BasicBlock] = []
        self.entry_block: Optional[BasicBlock] = None
        self.exit_block: Optional[BasicBlock] = None
        self.label_to_block: Dict[str, int] = {}
    
    def add_block(self, block: BasicBlock):
        """Add a basic block to CFG"""
        self.blocks.append(block)
    
    def get_block(self, block_id: int) -> Optional[BasicBlock]:
        """Get block by ID"""
        if 0 <= block_id < len(self.blocks):
            return self.blocks[block_id]
        return None
    
    def build_from_tac(self, instructions: List[TACInstruction]) -> 'ControlFlowGraph':
        """Build CFG from TAC instructions"""
        # Create entry block
        self.entry_block = BasicBlock(0)
        self.blocks.append(self.entry_block)
        
        current_block = self.entry_block
        block_id = 1
        
        # First pass: identify leaders (start of basic blocks)
        leaders = {0}  # First instruction is always a leader
        
        for i, instr in enumerate(instructions):
            # Target of jump is a leader
            if isinstance(instr, (TACGoto, TACConditionalGoto)):
                # Next instruction after jump is also a leader
                if i + 1 < len(instructions):
                    leaders.add(i + 1)
            elif isinstance(instr, TACLabel):
                # Label is a leader
                leaders.add(i)
                self.label_to_block[instr.label] = -1  # Will be filled later
        
        # Second pass: create basic blocks
        leaders_list = sorted(leaders)
        block_map = {}  # Map instruction index to block
        
        for i, leader_idx in enumerate(leaders_list):
            block = BasicBlock(i)
            block.start_index = leader_idx
            
            # Determine end index
            if i + 1 < len(leaders_list):
                block.end_index = leaders_list[i + 1] - 1
            else:
                block.end_index = len(instructions) - 1
            
            # Add instructions to block
            for instr_idx in range(block.start_index, block.end_index + 1):
                if instr_idx < len(instructions):
                    block.add_instruction(instructions[instr_idx])
                    block_map[instr_idx] = i
                    
                    # Map labels to blocks
                    if isinstance(instructions[instr_idx], TACLabel):
                        self.label_to_block[instructions[instr_idx].label] = i
            
            self.blocks.append(block)
        
        # Third pass: connect blocks (build edges)
        for block in self.blocks:
            if not block.instructions:
                continue
            
            last_instr = block.instructions[-1]
            
            if isinstance(last_instr, TACGoto):
                # Unconditional jump
                target_block = self.label_to_block.get(last_instr.label)
                if target_block is not None:
                    block.add_successor(target_block)
                    self.blocks[target_block].add_predecessor(block.id)
            
            elif isinstance(last_instr, TACConditionalGoto):
                # Conditional jump - two successors
                target_block = self.label_to_block.get(last_instr.label)
                if target_block is not None:
                    block.add_successor(target_block)
                    self.blocks[target_block].add_predecessor(block.id)
                
                # Fall-through to next block
                if block.id + 1 < len(self.blocks):
                    block.add_successor(block.id + 1)
                    self.blocks[block.id + 1].add_predecessor(block.id)
            
            elif not isinstance(last_instr, TACReturn):
                # Fall-through to next block
                if block.id + 1 < len(self.blocks):
                    block.add_successor(block.id + 1)
                    self.blocks[block.id + 1].add_predecessor(block.id)
        
        return self
    
    def compute_liveness(self):
        """Compute live variable analysis using iterative data flow"""
        # Initialize use and def sets for each block
        for block in self.blocks:
            for instr in block.instructions:
                # Get variables used and defined
                used_vars = self._get_used_vars(instr)
                defined_vars = self._get_defined_vars(instr)
                
                # Add to use set if not already defined in this block
                for var in used_vars:
                    if var not in block.def_vars:
                        block.use.add(var)
                
                # Add to def set
                for var in defined_vars:
                    block.def_vars.add(var)
        
        # Iterative fixed-point algorithm for live_in and live_out
        changed = True
        iterations = 0
        max_iterations = 100
        
        while changed and iterations < max_iterations:
            changed = False
            iterations += 1
            
            # Process blocks in reverse order
            for block in reversed(self.blocks):
                old_live_in = block.live_in.copy()
                old_live_out = block.live_out.copy()
                
                # live_out[B] = Union of live_in[S] for all successors S
                block.live_out = set()
                for succ_id in block.successors:
                    succ = self.blocks[succ_id]
                    block.live_out |= succ.live_in
                
                # live_in[B] = use[B] U (live_out[B] - def[B])
                block.live_in = block.use | (block.live_out - block.def_vars)
                
                if block.live_in != old_live_in or block.live_out != old_live_out:
                    changed = True
    
    def _get_used_vars(self, instr: TACInstruction) -> Set[str]:
        """Get variables used in an instruction"""
        used = set()
        
        if isinstance(instr, (TACBinaryOp, TACArrayAccess, TACTableAccess)):
            if hasattr(instr, 'arg1') and self._is_variable(instr.arg1):
                used.add(instr.arg1)
            if hasattr(instr, 'arg2') and self._is_variable(instr.arg2):
                used.add(instr.arg2)
        elif isinstance(instr, TACUnaryOp):
            if self._is_variable(instr.arg1):
                used.add(instr.arg1)
        elif isinstance(instr, TACAssignment):
            if self._is_variable(instr.arg1):
                used.add(instr.arg1)
        elif isinstance(instr, (TACArrayAssign, TACTableAssign)):
            if hasattr(instr, 'value') and self._is_variable(instr.value):
                used.add(instr.value)
            if hasattr(instr, 'index') and self._is_variable(instr.index):
                used.add(instr.index)
        elif isinstance(instr, TACConditionalGoto):
            if self._is_variable(instr.condition):
                used.add(instr.condition)
        elif isinstance(instr, TACReturn):
            if instr.value and self._is_variable(instr.value):
                used.add(instr.value)
        elif isinstance(instr, TACParam):
            if self._is_variable(instr.arg):
                used.add(instr.arg)
        
        return used
    
    def _get_defined_vars(self, instr: TACInstruction) -> Set[str]:
        """Get variables defined in an instruction"""
        defined = set()
        
        if isinstance(instr, (TACAssignment, TACBinaryOp, TACUnaryOp, 
                              TACArrayAccess, TACTableAccess, TACCast, TACAllocate)):
            if hasattr(instr, 'result') and self._is_variable(instr.result):
                defined.add(instr.result)
        elif isinstance(instr, TACFunctionCall):
            if instr.result and self._is_variable(instr.result):
                defined.add(instr.result)
        
        return defined
    
    def _is_variable(self, name: str) -> bool:
        """Check if a name is a variable (not a literal)"""
        if not name or not isinstance(name, str):
            return False
        # Check if it's a number literal
        try:
            float(name)
            return False
        except ValueError:
            pass
        # Check if it's a string literal
        if name.startswith('"') and name.endswith('"'):
            return False
        if name.startswith("'") and name.endswith("'"):
            return False
        # Check for boolean literals
        if name in ('true', 'false', 'True', 'False'):
            return False
        return True
    
    def __repr__(self):
        return f"CFG({len(self.blocks)} blocks)"
