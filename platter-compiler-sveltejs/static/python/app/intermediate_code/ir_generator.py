"""
Intermediate Representation Generator for Platter Language

This module generates both Three Address Code (TAC) and Quadruples
from the Abstract Syntax Tree (AST).
"""

from __future__ import annotations

from typing import List, Optional, Tuple, Any
import sys
import os

# Add parent directory to path for imports
app_dir = os.path.dirname(os.path.dirname(__file__))
python_dir = os.path.dirname(app_dir)
sys.path.insert(0, python_dir)

from app.semantic_analyzer.ast.ast_nodes import *
from .tac import *
from .quadruple import *


# AST compatibility aliases (supports both legacy and current AST node names)
VarDecl = globals().get("VarDecl", globals().get("IngrDecl"))
IfStatement = globals().get("IfStatement", globals().get("CheckStatement"))
WhileLoop = globals().get("WhileLoop", globals().get("RepeatLoop"))
DoWhileLoop = globals().get("DoWhileLoop", globals().get("OrderRepeatLoop"))
ForLoop = globals().get("ForLoop", globals().get("PassLoop"))
SwitchStatement = globals().get("SwitchStatement", globals().get("MenuStatement"))
ReturnStatement = globals().get("ReturnStatement", globals().get("ServeStatement"))
FunctionCall = globals().get("FunctionCall", globals().get("RecipeCall"))


class IRGenerator:
    """
    Generates intermediate representation from AST.
    Produces both TAC instructions and Quadruples.
    """
    
    def __init__(self):
        # TAC instructions list
        self.tac_instructions: List[TACInstruction] = []
        
        # Quadruple table
        self.quad_table = QuadrupleTable()
        
        # Temporary variable counter
        self.temp_count = 0
        
        # Label counter
        self.label_count = 0
        
        # Current function context
        self.current_function = None

        # Declared recipe names (used for parser-compat call fallback)
        self.recipe_names = set()
        
        # Loop stack for break/continue
        self.loop_stack: List[Tuple[str, str]] = []  # (continue_label, break_label)
    
    def new_temp(self) -> str:
        """Generate a new temporary variable name"""
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp
    
    def new_label(self, prefix: str = "L") -> str:
        """Generate a new label"""
        label = f"{prefix}{self.label_count}"
        self.label_count += 1
        return label
    
    def emit_tac(self, instruction: TACInstruction):
        """Emit a TAC instruction"""
        self.tac_instructions.append(instruction)
    
    def emit_quad(self, operator: str, arg1: Optional[str] = None,
                  arg2: Optional[str] = None, result: Optional[str] = None) -> int:
        """Emit a quadruple and return its index"""
        return self.quad_table.emit(operator, arg1, arg2, result)
    
    def emit_comment(self, comment: str):
        """Emit a comment in both TAC and quadruples"""
        self.emit_tac(TACComment(comment))
        self.emit_quad("comment", comment)
    
    # =========================================================================
    # Main entry point
    # =========================================================================
    
    def generate(self, ast: Program) -> Tuple[List[TACInstruction], QuadrupleTable]:
        """
        Generate intermediate representation from AST.
        Returns: (TAC instructions, Quadruple table)
        """
        self.emit_comment("=== Platter Program IR ===")
        
        # Generate code for global declarations
        if ast.global_decl:
            self.emit_comment("Global Declarations")
            for decl in ast.global_decl:
                self.visit_declaration(decl)
        
        # Generate code for recipe (function) declarations
        if ast.recipe_decl:
            self.recipe_names = {recipe.name for recipe in ast.recipe_decl}
            self.emit_comment("Recipe Declarations")
            for recipe in ast.recipe_decl:
                self.visit_recipe_decl(recipe)
        
        # Generate code for main start() platter
        if ast.start_platter:
            self.emit_comment("Main Program (start)")
            self.emit_tac(TACFunctionBegin("start"))
            self.emit_quad("begin_func", "start")
            
            self.visit_platter(ast.start_platter)
            
            self.emit_tac(TACFunctionEnd("start"))
            self.emit_quad("end_func", "start")
        
        return self.tac_instructions, self.quad_table
    
    # =========================================================================
    # Declarations
    # =========================================================================
    
    def visit_declaration(self, node: ASTNode):
        """Visit any declaration node"""
        if isinstance(node, VarDecl):
            self.visit_var_decl(node)
        elif isinstance(node, ArrayDecl):
            self.visit_array_decl(node)
        elif isinstance(node, TablePrototype):
            self.visit_table_prototype(node)
        elif isinstance(node, TableDecl):
            self.visit_table_decl(node)
    
    def visit_var_decl(self, node: ASTNode):
        """Generate IR for variable declaration"""
        if node.init_value:
            # Variable with initialization
            value_temp = self.visit_expression(node.init_value)
            self.emit_tac(TACAssignment(node.identifier, value_temp))
            self.emit_quad("=", value_temp, None, node.identifier)
        # Note: Simple declarations without init don't generate code
    
    def visit_array_decl(self, node: ArrayDecl):
        """Generate IR for array declaration"""
        if node.init_value and hasattr(node.init_value, 'elements'):
            size = len(node.init_value.elements)
            self.emit_tac(TACAllocate(node.identifier, size, "array"))
            self.emit_quad("allocate", "array", size, node.identifier)

            for i, element in enumerate(node.init_value.elements):
                value_temp = self.visit_expression(element)
                self.emit_tac(TACArrayAssign(node.identifier, str(i), value_temp))
                self.emit_quad("[]=", node.identifier, str(i), value_temp)
        elif node.init_value is not None:
            # Array initialized from expression (e.g., function call returning array)
            if isinstance(node.init_value, Identifier) and node.init_value.name in self.recipe_names:
                # Parser compatibility: some array init paths produce Identifier for zero-arg recipe calls
                call_temp = self.new_temp()
                self.emit_tac(TACFunctionCall(call_temp, node.init_value.name, 0))
                self.emit_quad("call", node.init_value.name, "0", call_temp)
                value_temp = call_temp
            else:
                value_temp = self.visit_expression(node.init_value)
            self.emit_tac(TACAssignment(node.identifier, value_temp))
            self.emit_quad("=", value_temp, None, node.identifier)
        # Note: uninitialized array declarations don't emit runtime code
    
    def visit_table_prototype(self, node: TablePrototype):
        """Generate IR for table prototype (type definition)"""
        # Table prototypes are type definitions, no runtime code
        self.emit_comment(f"Table type: {node.name}")
    
    def visit_table_decl(self, node: TableDecl):
        """Generate IR for table instance declaration"""
        self.emit_tac(TACAllocate(node.identifier, node.table_type, "table"))
        self.emit_quad("allocate", "table", node.table_type, node.identifier)
        
        if node.init_value and isinstance(node.init_value, TableLiteral):
            # Initialize table fields
            for field_name, value_expr in self._iter_table_field_inits(node.init_value.field_inits):
                value_temp = self.visit_expression(value_expr)
                self.emit_tac(TACTableAssign(node.identifier, field_name, value_temp))
                self.emit_quad(".=", node.identifier, field_name, value_temp)
    
    def visit_recipe_decl(self, node: RecipeDecl):
        """Generate IR for recipe (function) declaration"""
        self.current_function = node.name
        
        self.emit_comment(f"Recipe: {node.name}")
        self.emit_tac(TACFunctionBegin(node.name))
        self.emit_quad("begin_func", node.name)
        
        # Bind positional params (pushed by caller as p0, p1, ...) to declared names
        for i, param in enumerate(node.params):
            self.emit_tac(TACAssignment(param.identifier, f"p{i}"))
            self.emit_quad("=", f"p{i}", None, param.identifier)
        
        # Function body
        self.visit_platter(node.body)
        
        # Ensure function has return
        self.emit_tac(TACReturn(None))
        self.emit_quad("return")
        
        self.emit_tac(TACFunctionEnd(node.name))
        self.emit_quad("end_func", node.name)
        
        self.current_function = None
    
    # =========================================================================
    # Statements
    # =========================================================================
    
    def visit_platter(self, node: Platter):
        """Generate IR for platter (block statement)"""
        # Local declarations
        for decl in node.local_decls:
            if isinstance(decl, (VarDecl, ArrayDecl, TablePrototype, TableDecl)):
                self.visit_declaration(decl)
            else:
                self.visit_statement(decl)
        
        # Statements
        for stmt in node.statements:
            self.visit_statement(stmt)
    
    def visit_statement(self, node: ASTNode):
        """Visit any statement node"""
        if isinstance(node, Assignment):
            self.visit_assignment(node)
        elif isinstance(node, IfStatement):
            self.visit_if_statement(node)
        elif isinstance(node, WhileLoop):
            self.visit_while_loop(node)
        elif isinstance(node, DoWhileLoop):
            self.visit_do_while_loop(node)
        elif isinstance(node, ForLoop):
            self.visit_for_loop(node)
        elif isinstance(node, SwitchStatement):
            self.visit_switch_statement(node)
        elif isinstance(node, ReturnStatement):
            self.visit_return_statement(node)
        elif isinstance(node, BreakStatement):
            self.visit_break_statement()
        elif isinstance(node, ContinueStatement):
            self.visit_continue_statement()
        elif isinstance(node, ExpressionStatement):
            self.visit_expression_statement(node)
    
    def visit_assignment(self, node: Assignment):
        """Generate IR for assignment statement"""
        value_temp = self.visit_expression(node.value)
        
        # Handle different assignment operators
        if node.operator == "=":
            # Simple assignment
            target_addr = self.get_lvalue_address(node.target)
            self.emit_assignment(target_addr, value_temp, node.target)
        else:
            # Compound assignment (+=, -=, etc.)
            target_addr = self.get_lvalue_address(node.target)
            
            # Read current value
            if isinstance(node.target, ArrayAccess):
                current_temp = self.new_temp()
                index_temp = self.visit_expression(node.target.index)
                array_addr = self.get_lvalue_address(node.target.array)
                self.emit_tac(TACArrayAccess(current_temp, array_addr, index_temp))
                self.emit_quad("[]", array_addr, index_temp, current_temp)
            elif isinstance(node.target, TableAccess):
                current_temp = self.new_temp()
                table_addr = self.get_lvalue_address(node.target.table)
                self.emit_tac(TACTableAccess(current_temp, table_addr, node.target.field))
                self.emit_quad(".", table_addr, node.target.field, current_temp)
            else:
                current_temp = target_addr
            
            # Compute new value
            op = node.operator[:-1]  # Remove '=' from operator
            result_temp = self.new_temp()
            self.emit_tac(TACBinaryOp(result_temp, current_temp, op, value_temp))
            self.emit_quad(op, current_temp, value_temp, result_temp)
            
            # Assign back
            self.emit_assignment(target_addr, result_temp, node.target)
    
    def emit_assignment(self, target_addr: str, value: str, target_node: ASTNode):
        """Helper to emit assignment based on target type"""
        if isinstance(target_node, ArrayAccess):
            index_temp = self.visit_expression(target_node.index)
            array_addr = self.get_lvalue_address(target_node.array)
            self.emit_tac(TACArrayAssign(array_addr, index_temp, value))
            self.emit_quad("[]=", array_addr, index_temp, value)
        elif isinstance(target_node, TableAccess):
            table_addr = self.get_lvalue_address(target_node.table)
            self.emit_tac(TACTableAssign(table_addr, target_node.field, value))
            self.emit_quad(".=", table_addr, target_node.field, value)
        else:
            self.emit_tac(TACAssignment(target_addr, value))
            self.emit_quad("=", value, None, target_addr)
    
    def visit_if_statement(self, node: ASTNode):
        """Generate IR for if statement"""
        # Labels
        else_label = self.new_label("else")
        end_label = self.new_label("endif")
        
        # Evaluate condition
        cond_temp = self.visit_expression(node.condition)
        
        # If false, jump to else/elif/end
        self.emit_tac(TACConditionalGoto(cond_temp, else_label, negated=True))
        self.emit_quad("ifFalse", cond_temp, None, else_label)
        
        # Then block
        self.visit_platter(node.then_block)
        self.emit_tac(TACGoto(end_label))
        self.emit_quad("goto", None, None, end_label)
        
        # Else label
        self.emit_tac(TACLabel(else_label))
        self.emit_quad("label", else_label)
        
        # Handle elif clauses
        for elif_cond, elif_block in node.elif_clauses:
            next_elif_label = self.new_label("elif")
            
            elif_cond_temp = self.visit_expression(elif_cond)
            self.emit_tac(TACConditionalGoto(elif_cond_temp, next_elif_label, negated=True))
            self.emit_quad("ifFalse", elif_cond_temp, None, next_elif_label)
            
            self.visit_platter(elif_block)
            self.emit_tac(TACGoto(end_label))
            self.emit_quad("goto", None, None, end_label)
            
            self.emit_tac(TACLabel(next_elif_label))
            self.emit_quad("label", next_elif_label)
        
        # Else block
        if node.else_block:
            self.visit_platter(node.else_block)
        
        # End label
        self.emit_tac(TACLabel(end_label))
        self.emit_quad("label", end_label)
    
    def visit_while_loop(self, node: ASTNode):
        """Generate IR for while loop"""
        start_label = self.new_label("while_start")
        end_label = self.new_label("while_end")
        
        # Push loop context for break/continue
        self.loop_stack.append((start_label, end_label))
        
        # Start label
        self.emit_tac(TACLabel(start_label))
        self.emit_quad("label", start_label)
        
        # Evaluate condition
        cond_temp = self.visit_expression(node.condition)
        
        # If false, exit loop
        self.emit_tac(TACConditionalGoto(cond_temp, end_label, negated=True))
        self.emit_quad("ifFalse", cond_temp, None, end_label)
        
        # Loop body
        self.visit_platter(node.body)
        
        # Jump back to start
        self.emit_tac(TACGoto(start_label))
        self.emit_quad("goto", None, None, start_label)
        
        # End label
        self.emit_tac(TACLabel(end_label))
        self.emit_quad("label", end_label)
        
        self.loop_stack.pop()
    
    def visit_do_while_loop(self, node: ASTNode):
        """Generate IR for do-while loop"""
        start_label = self.new_label("do_start")
        continue_label = self.new_label("do_continue")
        end_label = self.new_label("do_end")
        
        self.loop_stack.append((continue_label, end_label))
        
        # Start label
        self.emit_tac(TACLabel(start_label))
        self.emit_quad("label", start_label)
        
        # Loop body
        self.visit_platter(node.body)
        
        # Continue label (for continue statements)
        self.emit_tac(TACLabel(continue_label))
        self.emit_quad("label", continue_label)
        
        # Evaluate condition
        cond_temp = self.visit_expression(node.condition)
        
        # If true, continue loop
        self.emit_tac(TACConditionalGoto(cond_temp, start_label, negated=False))
        self.emit_quad("if", cond_temp, None, start_label)
        
        # End label
        self.emit_tac(TACLabel(end_label))
        self.emit_quad("label", end_label)
        
        self.loop_stack.pop()
    
    def visit_for_loop(self, node: ASTNode):
        """Generate IR for for loop"""
        start_label = self.new_label("for_start")
        continue_label = self.new_label("for_continue")
        end_label = self.new_label("for_end")
        
        self.loop_stack.append((continue_label, end_label))
        
        # Initialization
        if node.init:
            self.visit_assignment(node.init)
        
        # Start label
        self.emit_tac(TACLabel(start_label))
        self.emit_quad("label", start_label)
        
        # Condition
        cond_temp = self.visit_expression(node.condition)
        self.emit_tac(TACConditionalGoto(cond_temp, end_label, negated=True))
        self.emit_quad("ifFalse", cond_temp, None, end_label)
        
        # Loop body
        self.visit_platter(node.body)
        
        # Continue label
        self.emit_tac(TACLabel(continue_label))
        self.emit_quad("label", continue_label)
        
        # Update
        if node.update:
            self.visit_assignment(node.update)
        
        # Jump back to start
        self.emit_tac(TACGoto(start_label))
        self.emit_quad("goto", None, None, start_label)
        
        # End label
        self.emit_tac(TACLabel(end_label))
        self.emit_quad("label", end_label)
        
        self.loop_stack.pop()
    
    def visit_switch_statement(self, node: ASTNode):
        """Generate IR for switch statement"""
        end_label = self.new_label("switch_end")
        
        # Evaluate switch expression
        expr_temp = self.visit_expression(node.expr)
        
        # Generate labels for each case
        case_labels = [self.new_label(f"case") for _ in node.cases]
        default_label = self.new_label("default") if node.default else end_label
        
        # Generate case comparisons
        for i, case in enumerate(node.cases):
            case_value_temp = self.visit_expression(case.value)
            cmp_temp = self.new_temp()
            
            self.emit_tac(TACBinaryOp(cmp_temp, expr_temp, "==", case_value_temp))
            self.emit_quad("==", expr_temp, case_value_temp, cmp_temp)
            
            self.emit_tac(TACConditionalGoto(cmp_temp, case_labels[i], negated=False))
            self.emit_quad("if", cmp_temp, None, case_labels[i])
        
        # Jump to default if no case matched
        self.emit_tac(TACGoto(default_label))
        self.emit_quad("goto", None, None, default_label)
        
        # Generate case bodies
        for i, case in enumerate(node.cases):
            self.emit_tac(TACLabel(case_labels[i]))
            self.emit_quad("label", case_labels[i])
            
            for stmt in case.statements:
                self.visit_statement(stmt)
            
            # Fall through to next case (unless break is encountered)
        
        # Default case
        if node.default:
            self.emit_tac(TACLabel(default_label))
            self.emit_quad("label", default_label)
            
            for stmt in node.default:
                self.visit_statement(stmt)
        
        # End label
        self.emit_tac(TACLabel(end_label))
        self.emit_quad("label", end_label)
    
    def visit_return_statement(self, node: ASTNode):
        """Generate IR for return statement"""
        if node.value:
            value_temp = self.visit_expression(node.value)
            self.emit_tac(TACReturn(value_temp))
            self.emit_quad("return", value_temp)
        else:
            self.emit_tac(TACReturn())
            self.emit_quad("return")
    
    def visit_break_statement(self):
        """Generate IR for break statement"""
        if self.loop_stack:
            _, break_label = self.loop_stack[-1]
            self.emit_tac(TACGoto(break_label))
            self.emit_quad("goto", None, None, break_label)
    
    def visit_continue_statement(self):
        """Generate IR for continue statement"""
        if self.loop_stack:
            continue_label, _ = self.loop_stack[-1]
            self.emit_tac(TACGoto(continue_label))
            self.emit_quad("goto", None, None, continue_label)
    
    def visit_expression_statement(self, node: ExpressionStatement):
        """Generate IR for expression statement"""
        # For array-transforming built-ins used as statements, write result back
        # to the first argument so calls like append(arr, x); update arr.
        if isinstance(node.expr, FunctionCall):
            result_temp = self.visit_function_call(node.expr)
            if (
                node.expr.name in {"append", "remove", "sort", "reverse"}
                and len(node.expr.args) >= 1
                and isinstance(node.expr.args[0], Identifier)
            ):
                target_name = node.expr.args[0].name
                self.emit_tac(TACAssignment(target_name, result_temp))
                self.emit_quad("=", result_temp, None, target_name)
            return

        self.visit_expression(node.expr)
    
    # =========================================================================
    # Expressions
    # =========================================================================
    
    def visit_expression(self, node: ASTNode) -> str:
        """
        Visit an expression node and return the temporary variable
        or identifier that holds the result.
        """
        if isinstance(node, BinaryOp):
            return self.visit_binary_op(node)
        elif isinstance(node, UnaryOp):
            return self.visit_unary_op(node)
        elif isinstance(node, Identifier):
            return node.name
        elif isinstance(node, Literal):
            return str(node.value)
        elif isinstance(node, ArrayAccess):
            return self.visit_array_access(node)
        elif isinstance(node, TableAccess):
            return self.visit_table_access(node)
        elif isinstance(node, FunctionCall):
            return self.visit_function_call(node)
        elif isinstance(node, CastExpr):
            return self.visit_cast_expr(node)
        elif isinstance(node, ArrayLiteral):
            return self.visit_array_literal(node)
        elif isinstance(node, TableLiteral):
            return self.visit_table_literal(node)
        else:
            # Unknown expression type
            temp = self.new_temp()
            self.emit_comment(f"Unknown expression: {type(node).__name__}")
            return temp
    
    def visit_binary_op(self, node: BinaryOp) -> str:
        """Generate IR for binary operation"""
        left_temp = self.visit_expression(node.left)
        right_temp = self.visit_expression(node.right)
        result_temp = self.new_temp()
        
        self.emit_tac(TACBinaryOp(result_temp, left_temp, node.operator, right_temp))
        self.emit_quad(node.operator, left_temp, right_temp, result_temp)
        
        return result_temp
    
    def visit_unary_op(self, node: UnaryOp) -> str:
        """Generate IR for unary operation"""
        operand_temp = self.visit_expression(node.operand)
        result_temp = self.new_temp()
        
        self.emit_tac(TACUnaryOp(result_temp, node.operator, operand_temp))
        if node.operator == "-":
            self.emit_quad("unary-", operand_temp, None, result_temp)
        else:
            self.emit_quad(node.operator, operand_temp, None, result_temp)
        
        return result_temp
    
    def visit_array_access(self, node: ArrayAccess) -> str:
        """Generate IR for array access"""
        array_temp = self.visit_expression(node.array)
        index_temp = self.visit_expression(node.index)
        result_temp = self.new_temp()
        
        self.emit_tac(TACArrayAccess(result_temp, array_temp, index_temp))
        self.emit_quad("[]", array_temp, index_temp, result_temp)
        
        return result_temp
    
    def visit_table_access(self, node: TableAccess) -> str:
        """Generate IR for table field access"""
        table_temp = self.visit_expression(node.table)
        result_temp = self.new_temp()
        
        self.emit_tac(TACTableAccess(result_temp, table_temp, node.field))
        self.emit_quad(".", table_temp, node.field, result_temp)
        
        return result_temp
    
    def visit_function_call(self, node: ASTNode) -> str:
        """Generate IR for function call"""
        # Evaluate and push arguments
        for arg in node.args:
            arg_temp = self.visit_expression(arg)
            self.emit_tac(TACParam(arg_temp))
            self.emit_quad("param", arg_temp)
        
        # Make the call
        result_temp = self.new_temp()
        self.emit_tac(TACFunctionCall(result_temp, node.name, len(node.args)))
        self.emit_quad("call", node.name, str(len(node.args)), result_temp)
        
        return result_temp
    
    def visit_cast_expr(self, node: CastExpr) -> str:
        """Generate IR for type cast"""
        expr_temp = self.visit_expression(node.expr)
        result_temp = self.new_temp()
        
        self.emit_tac(TACCast(result_temp, node.target_type, expr_temp))
        self.emit_quad("cast", node.target_type, expr_temp, result_temp)
        
        return result_temp
    
    def visit_array_literal(self, node: ArrayLiteral) -> str:
        """Generate IR for array literal"""
        # Simplified: allocate and initialize array
        result_temp = self.new_temp()
        size = str(len(node.elements))
        
        self.emit_tac(TACAllocate(result_temp, size, "array"))
        self.emit_quad("allocate", "array", size, result_temp)
        
        # Initialize elements
        for i, elem in enumerate(node.elements):
            elem_temp = self.visit_expression(elem)
            self.emit_tac(TACArrayAssign(result_temp, str(i), elem_temp))
            self.emit_quad("[]=", result_temp, str(i), elem_temp)
        
        return result_temp
    
    def visit_table_literal(self, node: TableLiteral) -> str:
        """Generate IR for table literal"""
        result_temp = self.new_temp()
        
        self.emit_tac(TACAllocate(result_temp, "table_literal", "table"))
        self.emit_quad("allocate", "table", "table_literal", result_temp)
        
        # Initialize fields
        for field_name, value_expr in self._iter_table_field_inits(node.field_inits):
            value_temp = self.visit_expression(value_expr)
            self.emit_tac(TACTableAssign(result_temp, field_name, value_temp))
            self.emit_quad(".=", result_temp, field_name, value_temp)
        
        return result_temp
    
    # =========================================================================
    # Helper methods
    # =========================================================================

    def _iter_table_field_inits(self, field_inits):
        """Yield (field_name, value_expr) from parser-produced table field tuples."""
        for item in field_inits:
            if isinstance(item, tuple) and len(item) >= 2:
                yield item[0], item[1]
    
    def get_lvalue_address(self, node: ASTNode) -> str:
        """Get the address (name) of an lvalue"""
        if isinstance(node, Identifier):
            return node.name
        elif isinstance(node, ArrayAccess):
            # For array access, return the array name (index handled separately)
            return self.get_lvalue_address(node.array)
        elif isinstance(node, TableAccess):
            # For table access, return the table name (field handled separately)
            return self.get_lvalue_address(node.table)
        else:
            # Fallback
            return self.new_temp()
