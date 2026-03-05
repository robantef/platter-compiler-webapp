"""
Type Checking Pass for Platter Language
Validates type compatibility in expressions, assignments, and operations
"""

from app.semantic_analyzer.ast.ast_nodes import *
from app.semantic_analyzer.symbol_table.types import TypeInfo, Symbol, SymbolKind
from app.semantic_analyzer.symbol_table.symbol_table import SymbolTable
from app.semantic_analyzer.semantic_passes.error_handler import SemanticErrorHandler, ErrorCodes
from app.semantic_analyzer.builtin_recipes import get_builtin_recipe, is_builtin_recipe, find_compatible_builtin_overload
from typing import Optional


class TypeChecker:
    """Performs type checking on AST"""
    
    def __init__(self, symbol_table: SymbolTable, error_handler: SemanticErrorHandler):
        self.symbol_table = symbol_table
        self.error_handler = error_handler
    
    def check(self, ast_root: Program):
        """Run type checking pass"""
        # Check global declarations
        for decl in ast_root.global_decl:
            if isinstance(decl, IngrDecl):
                self._check_ingr_decl(decl)
            elif isinstance(decl, ArrayDecl):
                self._check_array_decl(decl)
            elif isinstance(decl, TableDecl):
                self._check_table_decl(decl)
        
        # Check recipe bodies
        for recipe in ast_root.recipe_decl:
            self._check_recipe_decl(recipe)
        
        # Check start_platter if present (navigate to its existing scope)
        if ast_root.start_platter:
            if self.symbol_table.navigate_to_scope("start_platter"):
                self._check_platter(ast_root.start_platter)
                self.symbol_table.exit_scope()
    
    def _check_ingr_decl(self, node: IngrDecl):
        """Check ingredient declaration type consistency"""
        if node.init_value:
            # Special case: empty array literals are compatible with any array type
            if isinstance(node.init_value, ArrayLiteral) and not node.init_value.elements:
                ingredient_type = TypeInfo(node.data_type, 0)
                if ingredient_type.dimensions > 0:
                    # Empty array is compatible with any array type
                    return
            
            init_type = self._get_expression_type(node.init_value)
            if init_type:
                ingredient_type = TypeInfo(node.data_type, 0)
                if not ingredient_type.is_exact_match(init_type):
                    self.error_handler.add_error(
                        f"Type mismatch in ingredient '{node.identifier}' initialization: "
                        f"expected {ingredient_type}, got {init_type}",
                        node,
                        ErrorCodes.TYPE_MISMATCH
                    )
    
    def _check_array_decl(self, node: ArrayDecl):
        """Check array declaration type consistency"""
        if node.init_value:
            # Special case: empty array literals are compatible with any array type
            if isinstance(node.init_value, ArrayLiteral) and not node.init_value.elements:
                dims = node.dimensions if node.dimensions is not None else 0
                if dims > 0:
                    # Empty array is compatible with any array type
                    return
            
            # Create expected array type
            dims = node.dimensions if node.dimensions is not None else 0
            array_type = TypeInfo(node.data_type, dims)
            
            # Check if data_type is a valid type (primitive or table)
            if node.data_type not in ["piece", "sip", "chars", "flag"]:
                # It's a table type - check if it exists
                table_type = self.symbol_table.lookup_table_type(node.data_type)
                if not table_type:
                    self.error_handler.add_error(
                        f"Undefined table type '{node.data_type}'",
                        node,
                        ErrorCodes.UNDEFINED_TYPE
                    )
                    return
                # Mark it as a table type and add table fields
                array_type.is_table = True
                array_type.table_fields = table_type.table_fields
            
            # Get init type with expected type context for validation
            init_type = self._get_expression_type(node.init_value, array_type)
            if init_type:
                if not array_type.is_exact_match(init_type):
                    self.error_handler.add_error(
                        f"Type mismatch in array '{node.identifier}' initialization: "
                        f"expected {array_type}, got {init_type}",
                        node,
                        ErrorCodes.TYPE_MISMATCH
                    )
    
    def _check_table_decl(self, node: TableDecl):
        """Check table declaration type consistency"""
        # Verify table type exists
        table_type = self.symbol_table.lookup_table_type(node.table_type)
        if not table_type:
            self.error_handler.add_error(
                f"Undefined table type '{node.table_type}'",
                node,
                ErrorCodes.UNDEFINED_TYPE
            )
            return
        
        if node.init_value:
            # For table literals, check field-by-field instead of comparing types directly
            if isinstance(node.init_value, TableLiteral):
                # Validate each field in the literal
                for field_name, value, line, col in node.init_value.field_inits:
                    # Check if field exists in table type
                    if field_name not in table_type.table_fields:
                        self.error_handler.add_error(
                            f"Table type '{node.table_type}' has no field '{field_name}'",
                            node,
                            ErrorCodes.UNDEFINED_FIELD
                        )
                        continue
                    
                    # Check if field value type matches expected type
                    expected_field_type = table_type.table_fields[field_name]
                    actual_field_type = self._get_expression_type(value, expected_field_type)
                    
                    if actual_field_type and not expected_field_type.is_exact_match(actual_field_type):
                        self.error_handler.add_error(
                            f"Field '{field_name}' type mismatch: expected {expected_field_type}, got {actual_field_type}",
                            node,
                            ErrorCodes.TYPE_MISMATCH
                        )
            else:
                # For non-literal expressions, compare types
                init_type = self._get_expression_type(node.init_value)
                if init_type:
                    dims = node.dimensions if node.dimensions is not None else 0
                    expected_type = TypeInfo(node.table_type, dims, table_type.table_fields if dims == 0 else None)
                    if dims > 0:
                        expected_type.is_table = True
                        expected_type.table_fields = table_type.table_fields
                    
                    if not expected_type.is_compatible_with(init_type):
                        self.error_handler.add_error(
                            f"Type mismatch in table '{node.identifier}' initialization: "
                            f"expected {expected_type}, got {init_type}",
                            node,
                            ErrorCodes.TYPE_MISMATCH
                        )
    
    def _check_recipe_decl(self, node: RecipeDecl):
        """Check recipe declaration"""
        # Save current recipe context
        old_recipe = self.symbol_table.current_function
        recipe_symbol = self.symbol_table.lookup_symbol(node.name)
        self.symbol_table.current_function = recipe_symbol
        
        # Check recipe body (navigate to existing recipe scope)
        if node.body:
            scope_name = node.name  # The builder removed 'recipe_' prefix
            if self.symbol_table.navigate_to_scope(scope_name):
                self._check_platter(node.body)
                self.symbol_table.exit_scope()
        
        # Restore recipe context
        self.symbol_table.current_function = old_recipe
    
    def _check_platter(self, node: Platter):
        """Check block/compound statement"""
        # Check local declarations
        for decl in node.local_decls:
            if isinstance(decl, IngrDecl):
                self._check_ingr_decl(decl)
            elif isinstance(decl, ArrayDecl):
                self._check_array_decl(decl)
            elif isinstance(decl, TableDecl):
                self._check_table_decl(decl)
        
        # Check statements
        for stmt in node.statements:
            self._check_statement(stmt)
    
    def _check_statement(self, node: ASTNode):
        """Check a statement"""
        if isinstance(node, Assignment):
            self._check_assignment(node)
        elif isinstance(node, ServeStatement):
            self._check_serve_statement(node)
        elif isinstance(node, CheckStatement):
            self._check_check_statement(node)
        elif isinstance(node, MenuStatement):
            self._check_menu_statement(node)
        elif isinstance(node, RepeatLoop):
            self._check_repeat_loop(node)
        elif isinstance(node, OrderRepeatLoop):
            self._check_order_repeat_loop(node)
        elif isinstance(node, PassLoop):
            self._check_pass_loop(node)
        elif isinstance(node, Platter):
            self._check_platter(node)
        elif isinstance(node, ExpressionStatement):
            self._get_expression_type(node.expr)
    
    def _check_assignment(self, node: Assignment):
        """Check assignment type compatibility"""
        # Check if trying to assign to a recipe (which is not allowed)
        if isinstance(node.target, Identifier):
            symbol = self.symbol_table.lookup_symbol(node.target.name)
            if symbol and symbol.kind == SymbolKind.FUNCTION:
                self.error_handler.add_error(
                    f"Cannot assign to recipe '{node.target.name}'. Recipes are not assignable.",
                    node.target,
                    ErrorCodes.INVALID_ASSIGNMENT_TARGET
                )
                return
        
        target_type = self._get_expression_type(node.target)
        
        # Special case: empty array literals are compatible with any array type
        if isinstance(node.value, ArrayLiteral) and not node.value.elements:
            if target_type and target_type.dimensions > 0:
                # Empty array is compatible with any array type
                return
        
        # Pass target type as expected type for context-aware inference
        value_type = self._get_expression_type(node.value, target_type)
        print(f"DEBUG ASSIGN LINE {node.line}: target={target_type.__repr__()}, value_node={type(node.value)}, value_type={value_type.__repr__() if value_type else 'None'}, expected target_type={target_type}")
        
        if target_type and value_type:
            if not target_type.is_exact_match(value_type):
                self.error_handler.add_error(
                    f"Type mismatch in assignment: cannot assign {value_type} to {target_type}",
                    node.target,  # Use target node for better error location
                    ErrorCodes.TYPE_MISMATCH
                )
    
    def _check_serve_statement(self, node: ServeStatement):
        """Check serve statement type compatibility"""
        if not self.symbol_table.current_function:
            return  # Error will be caught by control_flow_checker
        
        expected_type = self.symbol_table.current_function.type_info
        
        if node.value:
            # Special case: table literals matching table types
            if isinstance(node.value, TableLiteral) and expected_type.is_table:
                # Validate each field in the literal
                table_type_symbol = self.symbol_table.lookup_table_type(expected_type.base_type)
                if table_type_symbol:
                    all_fields_valid = True
                    for field_name, value, line, col in node.value.field_inits:
                        # Check if field exists in table type
                        if field_name not in table_type_symbol.table_fields:
                            self.error_handler.add_error(
                                f"Table type '{expected_type.base_type}' has no field '{field_name}'",
                                node,
                                ErrorCodes.UNDEFINED_FIELD
                            )
                            all_fields_valid = False
                            continue
                        
                        # Check if field value type matches expected type
                        expected_field_type = table_type_symbol.table_fields[field_name]
                        actual_field_type = self._get_expression_type(value, expected_field_type)
                        
                        if actual_field_type and not expected_field_type.is_compatible_with(actual_field_type):
                            self.error_handler.add_error(
                                f"Field '{field_name}' type mismatch: expected {expected_field_type}, got {actual_field_type}",
                                node,
                                ErrorCodes.TYPE_MISMATCH
                            )
                            all_fields_valid = False
                    
                    # If all fields are valid, accept the table literal
                    if all_fields_valid:
                        return
            
            # Special case: empty array literals are compatible with any array type
            if isinstance(node.value, ArrayLiteral) and not node.value.elements:
                if expected_type.dimensions > 0:
                    # Empty array is compatible with any array type
                    return
                else:
                    self.error_handler.add_error(
                        f"Cannot serve empty array when recipe expects {expected_type}",
                        node,
                        ErrorCodes.INVALID_SERVE_TYPE
                    )
                    return
            
            actual_type = self._get_expression_type(node.value)
            if actual_type and not expected_type.is_exact_match(actual_type):
                self.error_handler.add_error(
                    f"Serve type mismatch: expected {expected_type}, got {actual_type}",
                    node,
                    ErrorCodes.INVALID_SERVE_TYPE
                )
        else:
            # Serving nothing - check if recipe expects void
            if expected_type.base_type != "void":
                self.error_handler.add_error(
                    f"Missing serve value: recipe expects {expected_type}",
                    node,
                    ErrorCodes.INVALID_SERVE_TYPE
                )
    
    def _check_check_statement(self, node: CheckStatement):
        """Check check statement (check/alt/instead)"""
        # Check condition must be a comparison expression (BinaryOp), not just a flag variable
        from app.semantic_analyzer.ast.ast_nodes import BinaryOp, Identifier
        
        cond_type = self._get_expression_type(node.condition)
        
        # First check if the type is not flag at all
        if cond_type and cond_type.base_type != "flag":
            self.error_handler.add_error(
                f"Check condition must be flag type, got {cond_type}",
                node.condition,
                ErrorCodes.TYPE_MISMATCH
            )
        # If it is flag type but just an identifier (not an expression)
        elif isinstance(node.condition, Identifier) and cond_type and cond_type.base_type == "flag":
            self.error_handler.add_error(
                f"Check condition must be flag bearing expression, not identifier",
                node.condition,
                ErrorCodes.TYPE_MISMATCH
            )
        
        # Check branches
        self._check_platter(node.then_block)
        for alt_cond, alt_block in node.elif_clauses:
            self._get_expression_type(alt_cond)
            self._check_platter(alt_block)
        if node.else_block:
            self._check_platter(node.else_block)
    
    def _check_menu_statement(self, node: MenuStatement):
        """Check menu statement (menu/choice/usual)"""
        # Get menu expression type
        menu_type = self._get_expression_type(node.expr)
        
        # Track choice values to detect duplicates
        seen_values = []
        
        # Check choices
        for case in node.cases:
            # Check choice value type matches menu expression type
            case_type = self._get_expression_type(case.value)
            if menu_type and case_type and not menu_type.is_compatible_with(case_type):
                self.error_handler.add_error(
                    f"Choice value type {case_type} does not match menu expression type {menu_type}",
                    case.value,
                    ErrorCodes.TYPE_MISMATCH
                )
            
            # Check for duplicate choice values
            if isinstance(case.value, Literal):
                value_str = str(case.value.value)
                if value_str in seen_values:
                    self.error_handler.add_error(
                        f"Duplicate choice value: {value_str}",
                        case.value,
                        ErrorCodes.DUPLICATE_SYMBOL
                    )
                else:
                    seen_values.append(value_str)
            
            # Check choice statements
            for stmt in case.statements:
                self._check_statement(stmt)
        
        # Check usual case
        if node.default:
            for stmt in node.default:
                self._check_statement(stmt)
    
    def _check_repeat_loop(self, node: RepeatLoop):
        """Check repeat loop"""
        cond_type = self._get_expression_type(node.condition)
        if cond_type and cond_type.base_type not in ["flag", "piece", "sip"]:
            self.error_handler.add_warning(
                f"Loop condition should be flag type, got {cond_type}",
                node.condition
            )
        self._check_platter(node.body)
    
    def _check_order_repeat_loop(self, node: OrderRepeatLoop):
        """Check order-repeat loop"""
        self._check_platter(node.body)
        cond_type = self._get_expression_type(node.condition)
        if cond_type and cond_type.base_type not in ["flag", "piece", "sip"]:
            self.error_handler.add_warning(
                f"Loop condition should be flag type, got {cond_type}",
                node.condition
            )
    
    def _check_pass_loop(self, node: PassLoop):
        """Check pass loop"""
        if node.init:
            if isinstance(node.init, Assignment):
                self._check_assignment(node.init)
        if node.condition:
            cond_type = self._get_expression_type(node.condition)
            if cond_type and cond_type.base_type not in ["flag", "piece", "sip"]:
                self.error_handler.add_warning(
                    f"Loop condition should be flag type, got {cond_type}",
                    node.condition
                )
        if node.update:
            if isinstance(node.update, Assignment):
                self._check_assignment(node.update)
        self._check_platter(node.body)
    
    def _get_expression_type(self, expr: ASTNode, expected_type: Optional[TypeInfo] = None) -> Optional[TypeInfo]:
        """Get the type of an expression
        
        Args:
            expr: The expression to get the type of
            expected_type: Optional expected type for context-aware inference
        """
        if expr is None:
            return None
        
        if isinstance(expr, Literal):
            return self._get_literal_type(expr)
        elif isinstance(expr, Identifier):
            return self._get_identifier_type(expr)
        elif isinstance(expr, BinaryOp):
            return self._get_binary_op_type(expr)
        elif isinstance(expr, UnaryOp):
            return self._get_unary_op_type(expr)
        elif isinstance(expr, ArrayAccess):
            return self._get_array_access_type(expr)
        elif isinstance(expr, TableAccess):
            return self._get_table_access_type(expr)
        elif isinstance(expr, RecipeCall):
            return self._get_recipe_call_type(expr)
        elif isinstance(expr, CastExpr):
            return self._get_cast_type(expr)
        elif isinstance(expr, ArrayLiteral):
            return self._get_array_literal_type(expr, expected_type)
        elif isinstance(expr, TableLiteral):
            return self._get_table_literal_type(expr, expected_type)
        
        return None
    
    def _get_literal_type(self, node: Literal) -> TypeInfo:
        """Get type of a literal"""
        return TypeInfo(node.value_type, 0)
    
    def _get_identifier_type(self, node: Identifier) -> Optional[TypeInfo]:
        """Get type of an identifier"""
        symbol = self.symbol_table.lookup_symbol(node.name)
        if not symbol:
            return None
        return symbol.type_info
    
    def _get_binary_op_type(self, node: BinaryOp) -> Optional[TypeInfo]:
        """Get type of a binary operation"""
        left_type = self._get_expression_type(node.left)
        right_type = self._get_expression_type(node.right)
        
        if not left_type or not right_type:
            return None
        
        # Check for division by zero
        if node.operator in ['/', '%']:
            if isinstance(node.right, Literal):
                # Check if literal is zero
                if node.right.value_type in ["piece", "sip"]:
                    try:
                        value = float(node.right.value) if node.right.value_type == "sip" else int(node.right.value)
                        if value == 0:
                            self.error_handler.add_error(
                                f"Cannot divide by 0",
                                node,
                                ErrorCodes.DIVISION_BY_ZERO
                            )
                            return None
                    except (ValueError, TypeError):
                        pass  # If we can't parse the value, let other checks handle it
        
        # Determine result type based on operator
        if node.operator in ['+', '-', '*', '/', '%']:
            # Arithmetic operations require exact type match (no implicit conversions)
            if not left_type.is_exact_match(right_type):
                self.error_handler.add_error(
                    f"Type mismatch in binary operation: {left_type} {node.operator} {right_type}",
                    node,
                    ErrorCodes.INVALID_OPERATION
                )
                return None
            
            if left_type.base_type in ["piece", "sip"]:
                return left_type
            elif left_type.base_type == "chars" and node.operator == '+':
                # String concatenation
                return left_type
            else:
                self.error_handler.add_error(
                    f"Invalid type for arithmetic operation: {left_type}",
                    node,
                    ErrorCodes.INVALID_OPERATION
                )
                return None
        elif node.operator in ['<', '>', '<=', '>=']:
            # Relational operations require exact type match (no implicit conversions)
            if not left_type.is_exact_match(right_type):
                self.error_handler.add_error(
                    f"Type mismatch in binary operation: {left_type} {node.operator} {right_type}",
                    node,
                    ErrorCodes.INVALID_OPERATION
                )
                return None
            # Relational operations return flag (boolean)
            return TypeInfo("flag", 0)
        elif node.operator in ['==', '!=']:
            # Equality operations require exact type match
            if not left_type.is_exact_match(right_type):
                self.error_handler.add_error(
                    f"Type mismatch in binary operation: {left_type} {node.operator} {right_type}",
                    node,
                    ErrorCodes.INVALID_OPERATION
                )
                return None
            # Equality operations return flag (boolean)
            return TypeInfo("flag", 0)
        elif node.operator in ['and', 'or']:
            # Logical operations only work with flag types
            if left_type.base_type != "flag" or right_type.base_type != "flag":
                self.error_handler.add_error(
                    f"Logical operators require flag operands: {left_type} {node.operator} {right_type}",
                    node,
                    ErrorCodes.INVALID_OPERATION
                )
                return None
            if not left_type.is_exact_match(right_type):
                self.error_handler.add_error(
                    f"Type mismatch in binary operation: {left_type} {node.operator} {right_type}",
                    node,
                    ErrorCodes.INVALID_OPERATION
                )
                return None
            return TypeInfo("flag", 0)
        else:
            # For other operators, check exact match
            if not left_type.is_exact_match(right_type):
                self.error_handler.add_error(
                    f"Type mismatch in binary operation: {left_type} {node.operator} {right_type}",
                    node,
                    ErrorCodes.INVALID_OPERATION
                )
                return None
            return left_type
    
    def _get_unary_op_type(self, node: UnaryOp) -> Optional[TypeInfo]:
        """Get type of a unary operation"""
        operand_type = self._get_expression_type(node.operand)
        
        if not operand_type:
            return None
        
        if node.operator == '!':
            # Logical NOT
            return TypeInfo("flag", 0)
        elif node.operator in ['-', '+']:
            # Unary plus/minus
            if operand_type.base_type in ["piece", "sip"]:
                return operand_type
            else:
                self.error_handler.add_error(
                    f"Invalid type for unary {node.operator}: {operand_type}",
                    node,
                    ErrorCodes.INVALID_OPERATION
                )
                return None
        
        return operand_type
    
    def _get_array_access_type(self, node: ArrayAccess) -> Optional[TypeInfo]:
        """Get type of array access"""
        array_type = self._get_expression_type(node.array)
        index_type = self._get_expression_type(node.index)
        
        if not array_type:
            return None
        
        # Check index is integer type
        if index_type and index_type.base_type not in ["piece"]:
            self.error_handler.add_error(
                f"Array index must be piece type, got {index_type}",
                node.index,
                ErrorCodes.INVALID_ARRAY_ACCESS
            )
        
        # Check array is actually an array
        if array_type.dimensions == 0:
            self.error_handler.add_error(
                f"Cannot index non-array type {array_type}",
                node,
                ErrorCodes.INVALID_ARRAY_ACCESS
            )
            return None
        
        # Bounds checking for constant indices
        if isinstance(node.index, Literal) and node.index.value_type == "piece":
            try:
                index_value = int(node.index.value)
                # Get the array size if available
                if array_type.array_sizes and len(array_type.array_sizes) > 0:
                    array_size = array_type.array_sizes[0]
                    if index_value < 0 or index_value >= array_size:
                        self.error_handler.add_error(
                            f"Array index {index_value} out of bounds (array size: {array_size})",
                            node.index,
                            ErrorCodes.ARRAY_OUT_OF_BOUNDS
                        )
                else:
                    # Array has no size information - treat as uninitialized/empty array (size 0)
                    # Any access to an uninitialized array is out of bounds
                    self.error_handler.add_error(
                        f"Array index {index_value} out of bounds (array is uninitialized/empty, size: 0)",
                        node.index,
                        ErrorCodes.ARRAY_OUT_OF_BOUNDS
                    )
            except (ValueError, TypeError):
                # If we can't convert to int, skip bounds checking
                pass
        
        # Return element type
        return array_type.get_element_type()
    
    def _get_table_access_type(self, node: TableAccess) -> Optional[TypeInfo]:
        """Get type of table field access"""
        table_type = self._get_expression_type(node.table)
        
        if not table_type:
            return None
        
        # Check table is actually a table type
        if not table_type.is_table:
            self.error_handler.add_error(
                f"Cannot access field of non-table type {table_type}",
                node,
                ErrorCodes.INVALID_TABLE_ACCESS
            )
            return None
        
        # Get field type
        field_type = table_type.get_field_type(node.field)
        if not field_type:
            self.error_handler.add_error(
                f"Table type {table_type.base_type} has no field '{node.field}'",
                node,
                ErrorCodes.UNDEFINED_FIELD
            )
            return None
        
        return field_type
    
    def _get_recipe_call_type(self, node: RecipeCall) -> Optional[TypeInfo]:
        """Get type of recipe call (serve type)"""
        # Check if it's a built-in recipe
        if is_builtin_recipe(node.name):
            # Get argument types
            arg_types = []
            for arg in node.args:
                arg_type = self._get_expression_type(arg)
                if arg_type:
                    arg_types.append((arg_type.base_type, arg_type.dimensions))
                else:
                    # If we can't determine arg type, we can't find overload
                    return None
            
            # Find matching overload
            builtin_overload = find_compatible_builtin_overload(node.name, arg_types)
            if builtin_overload:
                # Validate built-in recipe constraints
                self._validate_builtin_recipe_call(node)
                return builtin_overload.get_return_type_info()
            else:
                # No matching overload found - error will be caught elsewhere
                return None
        
        # Look up user-defined recipe
        recipe_symbol = self.symbol_table.lookup_symbol(node.name)
        if not recipe_symbol:
            return None
        
        return recipe_symbol.type_info
    
    def _validate_builtin_recipe_call(self, node: RecipeCall):
        """Validate built-in recipe calls with strict parameter constraints"""
        
        # sqrt: argument must be non-negative
        if node.name == "sqrt" and len(node.args) > 0:
            arg = node.args[0]
            if isinstance(arg, Literal):
                try:
                    value = float(arg.value)
                    if value < 0:
                        self.error_handler.add_error(
                            f"sqrt() requires non-negative argument, got {value}",
                            arg,
                            ErrorCodes.INVALID_OPERATION
                        )
                except (ValueError, TypeError):
                    pass
        
        # fact: argument must be non-negative piece
        elif node.name == "fact" and len(node.args) > 0:
            arg = node.args[0]
            if isinstance(arg, Literal):
                try:
                    value = int(arg.value)
                    if value < 0:
                        self.error_handler.add_error(
                            f"fact() requires non-negative piece argument, got {value}",
                            arg,
                            ErrorCodes.INVALID_OPERATION
                        )
                except (ValueError, TypeError):
                    pass
        
        # cut: both arguments must be non-negative
        elif node.name == "cut" and len(node.args) == 2:
            for i, arg in enumerate(node.args):
                if isinstance(arg, Literal):
                    try:
                        value = float(arg.value)
                        if value < 0:
                            self.error_handler.add_error(
                                f"cut() requires non-negative arguments, got {value} at position {i+1}",
                                arg,
                                ErrorCodes.INVALID_OPERATION
                            )
                    except (ValueError, TypeError):
                        pass
        
        # copy: start and end indices must be non-negative
        elif node.name == "copy" and len(node.args) == 3:
            for i in [1, 2]:  # Check 2nd and 3rd arguments (indices)
                arg = node.args[i]
                if isinstance(arg, Literal):
                    try:
                        value = int(arg.value)
                        if value < 0:
                            param_name = "start" if i == 1 else "end"
                            self.error_handler.add_error(
                                f"copy() requires non-negative {param_name} index, got {value}",
                                arg,
                                ErrorCodes.INVALID_OPERATION
                            )
                    except (ValueError, TypeError):
                        pass
        
        # sort: must be 1-dimensional array
        elif node.name == "sort" and len(node.args) > 0:
            arg_type = self._get_expression_type(node.args[0])
            if arg_type and arg_type.dimensions != 1:
                self.error_handler.add_error(
                    f"sort() requires 1-dimensional array, got {arg_type.dimensions}-dimensional array",
                    node.args[0],
                    ErrorCodes.INVALID_OPERATION
                )
        
        # remove: index must be non-negative and less than array size
        elif node.name == "remove" and len(node.args) == 2:
            index_arg = node.args[1]
            array_arg = node.args[0]
            
            # Check if index is non-negative
            if isinstance(index_arg, Literal):
                try:
                    index_value = int(index_arg.value)
                    if index_value < 0:
                        self.error_handler.add_error(
                            f"remove() requires non-negative index, got {index_value}",
                            index_arg,
                            ErrorCodes.INVALID_OPERATION
                        )
                    else:
                        # Check bounds if we can determine array size
                        array_type = self._get_expression_type(array_arg)
                        if array_type and array_type.array_sizes and len(array_type.array_sizes) > 0:
                            array_size = array_type.array_sizes[0]
                            if index_value >= array_size:
                                self.error_handler.add_error(
                                    f"remove() index {index_value} out of bounds (array size: {array_size})",
                                    index_arg,
                                    ErrorCodes.ARRAY_OUT_OF_BOUNDS
                                )
                except (ValueError, TypeError):
                    pass
        
        # matches: both arguments must have same type and dimensions (any dimensions allowed)
        elif node.name == "matches" and len(node.args) == 2:
            arg1_type = self._get_expression_type(node.args[0])
            arg2_type = self._get_expression_type(node.args[1])
            
            if arg1_type and arg2_type:
                # Check if types match (base type and dimensions)
                if arg1_type.base_type != arg2_type.base_type:
                    self.error_handler.add_error(
                        f"matches() requires both arguments to have same base type, got {arg1_type.base_type} and {arg2_type.base_type}",
                        node,
                        ErrorCodes.TYPE_MISMATCH
                    )
                elif arg1_type.dimensions != arg2_type.dimensions:
                    self.error_handler.add_error(
                        f"matches() requires both arguments to have same dimensions, got {arg1_type.dimensions}D and {arg2_type.dimensions}D",
                        node,
                        ErrorCodes.TYPE_MISMATCH
                    )
    
    def _get_cast_type(self, node: CastExpr) -> TypeInfo:
        """Get type of cast expression"""
        dims = node.dimensions if node.dimensions is not None else 0
        
        # Check if cast is valid
        expr_type = self._get_expression_type(node.expr)
        target_type = TypeInfo(node.target_type, dims)
        
        if expr_type:
            # Allow numeric conversions
            if expr_type.base_type in ["piece", "sip"] and target_type.base_type in ["piece", "sip"]:
                return target_type
            # Allow same-dimension array casts if base types compatible
            elif expr_type.dimensions == target_type.dimensions:
                if expr_type.base_type != target_type.base_type:
                    self.error_handler.add_warning(
                        f"Explicit cast from {expr_type} to {target_type}",
                        node
                    )
                return target_type
            else:
                self.error_handler.add_error(
                    f"Invalid cast from {expr_type} to {target_type}",
                    node,
                    ErrorCodes.INVALID_CAST
                )
        
        return target_type
    
    def _get_array_literal_type(self, node: ArrayLiteral, expected_type: Optional[TypeInfo] = None) -> Optional[TypeInfo]:
        """Get type of array literal
        
        Args:
            node: The array literal node
            expected_type: Optional expected array type for context-aware inference
        """
        if not node.elements:
            # Empty array literal - treat as 1D array of unknown base type
            # This allows dimension checking for nested empty arrays like [[],[]]
            return TypeInfo("unknown", 1)
        
        # Determine expected element type if we have an expected array type
        expected_element_type = None
        if expected_type and expected_type.dimensions > 0:
            expected_element_type = expected_type.get_element_type()
        
        # Get type of first element with expected type context
        first_type = self._get_expression_type(node.elements[0], expected_element_type)
        if not first_type:
            return None
        
        # Check all elements have same type
        for elem in node.elements[1:]:
            elem_type = self._get_expression_type(elem, expected_element_type)
            if elem_type and not first_type.is_compatible_with(elem_type):
                self.error_handler.add_error(
                    f"Array literal has inconsistent element types: {first_type} and {elem_type}",
                    node,
                    ErrorCodes.TYPE_MISMATCH
                )
        
        # Return array type with one more dimension
        return TypeInfo(first_type.base_type, first_type.dimensions + 1, first_type.table_fields if first_type.is_table else None)
    
    def _get_table_literal_type(self, node: TableLiteral, expected_type: Optional[TypeInfo] = None) -> Optional[TypeInfo]:
        """Get type of table literal
        
        Args:
            node: The table literal node
            expected_type: Optional expected table type for context-aware inference
        """
        # If expected type is a table type, use it for inference
        if expected_type and expected_type.is_table:
            # Look up the table type definition
            table_type_symbol = self.symbol_table.lookup_table_type(expected_type.base_type)
            if table_type_symbol and table_type_symbol.table_fields:
                # Validate literal fields against expected table type
                for field_name, value, line, col in node.field_inits:
                    expected_field_type = table_type_symbol.table_fields.get(field_name)
                    if expected_field_type:
                        # Get actual field type and validate
                        field_type = self._get_expression_type(value, expected_field_type)
                        if field_type and not expected_field_type.is_exact_match(field_type):
                            self.error_handler.add_error(
                                f"Type mismatch in table literal: field '{field_name}' expects {expected_field_type}, got {field_type}",
                                node,
                                ErrorCodes.TYPE_MISMATCH
                            )
                # Return the expected table type
                return TypeInfo(expected_type.base_type, 0, table_type_symbol.table_fields)
        
        # Fallback: Build field types from literal
        field_types = {}
        for field_name, value, line, col in node.field_inits:
            field_type = self._get_expression_type(value)
            if field_type:
                field_types[field_name] = field_type
        
        # Create synthetic table type
        return TypeInfo("anonymous_table", 0, field_types)
