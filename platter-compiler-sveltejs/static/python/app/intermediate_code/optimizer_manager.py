"""
Optimizer Manager

Coordinates multiple optimization passes and applies them in the correct order.
Supports iterative optimization until a fixed point is reached.
"""

from typing import List, Dict, Any
from .optimizer import OptimizationPass
from .tac import TACInstruction
from .quadruple import QuadrupleTable
from .constant_folding import ConstantFoldingPass
from .propagation import ConstantPropagationPass, CopyPropagationPass
from .dead_code_elimination import DeadCodeEliminationPass, UnreachableCodeEliminationPass
from .algebraic_simplification import AlgebraicSimplificationPass, StrengthReductionPass


class OptimizationLevel:
    """Optimization level constants"""
    NONE = 0
    BASIC = 1
    STANDARD = 2
    AGGRESSIVE = 3


class OptimizerManager:
    """Manages and applies optimization passes"""
    
    def __init__(self, optimization_level: int = OptimizationLevel.STANDARD):
        self.optimization_level = optimization_level
        self.passes: List[OptimizationPass] = []
        self.max_iterations = 10
        self.stats: Dict[str, Any] = {}
        
        self._configure_passes()
    
    def _configure_passes(self):
        """Configure optimization passes based on level"""
        if self.optimization_level == OptimizationLevel.NONE:
            return
        
        if self.optimization_level >= OptimizationLevel.BASIC:
            # Basic optimizations
            self.passes.append(ConstantFoldingPass())
            self.passes.append(DeadCodeEliminationPass())
        
        if self.optimization_level >= OptimizationLevel.STANDARD:
            # Standard optimizations
            self.passes.append(AlgebraicSimplificationPass())
            self.passes.append(ConstantPropagationPass())
            self.passes.append(CopyPropagationPass())
            self.passes.append(DeadCodeEliminationPass())
        
        if self.optimization_level >= OptimizationLevel.AGGRESSIVE:
            # Aggressive optimizations
            self.passes.append(StrengthReductionPass())
            self.passes.append(UnreachableCodeEliminationPass())
    
    def add_pass(self, pass_obj: OptimizationPass):
        """Add a custom optimization pass"""
        self.passes.append(pass_obj)
    
    def optimize_tac(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """
        Optimize TAC instructions
        
        Args:
            instructions: List of TAC instructions
            
        Returns:
            Optimized list of TAC instructions
        """
        if self.optimization_level == OptimizationLevel.NONE:
            return instructions
        
        optimized = instructions
        total_iterations = 0
        total_changes = 0
        
        # Iteratively apply passes until no more changes
        for iteration in range(self.max_iterations):
            iteration_changes = 0
            
            for pass_obj in self.passes:
                before_length = len(optimized)
                optimized = pass_obj.optimize_tac(optimized)
                iteration_changes += pass_obj.changes_made
                
                # Track stats per pass
                if pass_obj.name not in self.stats:
                    self.stats[pass_obj.name] = {
                        'changes': 0,
                        'applications': 0
                    }
                
                self.stats[pass_obj.name]['changes'] += pass_obj.changes_made
                self.stats[pass_obj.name]['applications'] += 1
            
            total_changes += iteration_changes
            total_iterations = iteration + 1
            
            # If no changes made, we've reached a fixed point
            if iteration_changes == 0:
                break
        
        self.stats['total_iterations'] = total_iterations
        self.stats['total_changes'] = total_changes
        self.stats['original_size'] = len(instructions)
        self.stats['optimized_size'] = len(optimized)
        
        return optimized
    
    def optimize_quads(self, quad_table: QuadrupleTable) -> QuadrupleTable:
        """
        Optimize quadruples
        
        Args:
            quad_table: Quadruple table
            
        Returns:
            Optimized quadruple table
        """
        if self.optimization_level == OptimizationLevel.NONE:
            return quad_table
        
        optimized = quad_table
        total_iterations = 0
        total_changes = 0
        
        for iteration in range(self.max_iterations):
            iteration_changes = 0
            
            for pass_obj in self.passes:
                optimized = pass_obj.optimize_quads(optimized)
                iteration_changes += pass_obj.changes_made
                
                if pass_obj.name not in self.stats:
                    self.stats[pass_obj.name] = {
                        'changes': 0,
                        'applications': 0
                    }
                
                self.stats[pass_obj.name]['changes'] += pass_obj.changes_made
                self.stats[pass_obj.name]['applications'] += 1
            
            total_changes += iteration_changes
            total_iterations = iteration + 1
            
            if iteration_changes == 0:
                break
        
        self.stats['total_iterations'] = total_iterations
        self.stats['total_changes'] = total_changes
        self.stats['original_size'] = len(quad_table.quadruples)
        self.stats['optimized_size'] = len(optimized.quadruples)
        
        return optimized
    
    def get_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        return self.stats
    
    def print_stats(self):
        """Print optimization statistics"""
        print("\n" + "="*60)
        print("OPTIMIZATION STATISTICS")
        print("="*60)
        
        print(f"\nOptimization Level: {self._get_level_name()}")
        print(f"Total Iterations: {self.stats.get('total_iterations', 0)}")
        print(f"Total Changes: {self.stats.get('total_changes', 0)}")
        print(f"Original Size: {self.stats.get('original_size', 0)} instructions")
        print(f"Optimized Size: {self.stats.get('optimized_size', 0)} instructions")
        
        reduction = self.stats.get('original_size', 0) - self.stats.get('optimized_size', 0)
        if self.stats.get('original_size', 0) > 0:
            percent = (reduction / self.stats.get('original_size', 1)) * 100
            print(f"Reduction: {reduction} instructions ({percent:.1f}%)")
        
        print("\nPer-Pass Statistics:")
        print("-" * 60)
        for pass_name, stats in self.stats.items():
            if isinstance(stats, dict) and 'changes' in stats:
                print(f"  {pass_name}:")
                print(f"    Changes: {stats['changes']}")
                print(f"    Applications: {stats['applications']}")
        
        print("="*60 + "\n")
    
    def _get_level_name(self) -> str:
        """Get the name of the current optimization level"""
        levels = {
            OptimizationLevel.NONE: "None (O0)",
            OptimizationLevel.BASIC: "Basic (O1)",
            OptimizationLevel.STANDARD: "Standard (O2)",
            OptimizationLevel.AGGRESSIVE: "Aggressive (O3)"
        }
        return levels.get(self.optimization_level, "Unknown")
    
    def reset_stats(self):
        """Reset optimization statistics"""
        self.stats = {}


def optimize_ir(instructions: List[TACInstruction], 
                quad_table: QuadrupleTable,
                level: int = OptimizationLevel.STANDARD,
                verbose: bool = True) -> tuple:
    """
    Convenience function to optimize both TAC and quadruples
    
    Args:
        instructions: TAC instructions
        quad_table: Quadruple table
        level: Optimization level
        verbose: Print statistics
        
    Returns:
        Tuple of (optimized_tac, optimized_quads, stats)
    """
    manager = OptimizerManager(level)
    
    optimized_tac = manager.optimize_tac(instructions)
    
    # Reset stats and optimize quads
    stats_tac = manager.get_stats()
    manager.reset_stats()
    
    optimized_quads = manager.optimize_quads(quad_table)
    stats_quads = manager.get_stats()
    
    if verbose:
        print("\n[TAC Optimization]")
        manager.stats = stats_tac
        manager.print_stats()
        
        print("\n[Quadruple Optimization]")
        manager.stats = stats_quads
        manager.print_stats()
    
    return optimized_tac, optimized_quads, {'tac': stats_tac, 'quads': stats_quads}
