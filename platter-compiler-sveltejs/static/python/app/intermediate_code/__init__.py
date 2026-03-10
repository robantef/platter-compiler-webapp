"""
Intermediate Code Generation Package for Platter Language

This package provides tools for generating intermediate representation (IR)
from the Platter language Abstract Syntax Tree (AST).

Modules:
- tac: Three Address Code instruction definitions
- quadruple: Quadruple representation and table
- ir_generator: Main IR generator that traverses AST
- output_formatter: Formatting and output utilities for IR
- optimizer: Base optimization infrastructure
- constant_folding: Constant folding optimization pass
- propagation: Constant and copy propagation passes
- dead_code_elimination: Dead code elimination passes
- algebraic_simplification: Algebraic simplification and strength reduction
- optimizer_manager: Manages and coordinates optimization passes
"""

from .tac import *
from .quadruple import *
from .ir_generator import IRGenerator
from .output_formatter import IRFormatter, format_tac, format_quadruples, format_ir
from .optimizer import OptimizationPass, BasicBlock, ControlFlowGraph
from .constant_folding import ConstantFoldingPass
from .propagation import ConstantPropagationPass, CopyPropagationPass
from .dead_code_elimination import DeadCodeEliminationPass, UnreachableCodeEliminationPass
from .algebraic_simplification import AlgebraicSimplificationPass, StrengthReductionPass
from .optimizer_manager import OptimizerManager, OptimizationLevel, optimize_ir
from .ir_interpreter import TACInterpreter, run_tac

__all__ = [
    # TAC Instructions
    'TACInstruction',
    'TACAssignment',
    'TACBinaryOp',
    'TACUnaryOp',
    'TACArrayAccess',
    'TACArrayAssign',
    'TACTableAccess',
    'TACTableAssign',
    'TACLabel',
    'TACGoto',
    'TACConditionalGoto',
    'TACFunctionCall',
    'TACParam',
    'TACReturn',
    'TACFunctionBegin',
    'TACFunctionEnd',
    'TACComment',
    'TACAllocate',
    'TACCast',
    'TACNop',
    
    # Quadruple
    'Quadruple',
    'QuadrupleTable',
    'create_binary_quad',
    'create_unary_quad',
    'create_assign_quad',
    'create_goto_quad',
    'create_if_quad',
    'create_label_quad',
    'create_param_quad',
    'create_call_quad',
    'create_return_quad',
    'create_array_read_quad',
    'create_array_write_quad',
    'create_table_read_quad',
    'create_table_write_quad',
    
    # IR Generator
    'IRGenerator',
    
    # Formatters
    'IRFormatter',
    'format_tac',
    'format_quadruples',
    'format_ir',
    
    # Optimization Base
    'OptimizationPass',
    'BasicBlock',
    'ControlFlowGraph',
    
    # Optimization Passes
    'ConstantFoldingPass',
    'ConstantPropagationPass',
    'CopyPropagationPass',
    'DeadCodeEliminationPass',
    'UnreachableCodeEliminationPass',
    'AlgebraicSimplificationPass',
    'StrengthReductionPass',
    
    # Optimizer Manager
    'OptimizerManager',
    'OptimizationLevel',
    'optimize_ir',
]

__version__ = '1.0.0'
