"""
Symbol Table Builder for Platter Language
Handles scoping and symbol collection - traverses AST to build symbol table structure
NOTE: This version does NOT perform semantic checking - it only collects symbols
"""

from app.semantic_analyzer.ast.ast_nodes import *
from app.semantic_analyzer.symbol_table.types import Symbol, Scope, SymbolKind, TypeInfo
from app.semantic_analyzer.symbol_table.symbol_table import SymbolTable
from app.semantic_analyzer.builtin_recipes import BUILTIN_RECIPES
from typing import Optional


class _BuiltinParam:
    """Simple parameter holder for built-in recipes"""
    def __init__(self, data_type: str, dimensions: int):
        self.data_type = data_type
        self.dimensions = dimensions


class _BuiltinDeclaration:
    """Simple declaration node holder for built-in recipes"""
    def __init__(self, params: list, return_type: str, return_dims: int):
        self.params = params
        self.return_type = return_type
        self.return_dims = return_dims


class SymbolTableBuilder:
    """Builds symbol table by traversing the AST - NO semantic checking!"""
    
    def __init__(self):
        self.symbol_table = SymbolTable()
    
    def _create_default_value(self, data_type: str, dimensions: int = 0):
        """Create default value for uninitialized declarations"""
        if dimensions > 0:
            # Create nested empty array literal
            return ArrayLiteral([])
        else:
            # Primitive types
            if data_type == "chars":
                return Literal("chars", "")
            elif data_type == "piece":
                return Literal("piece", 0)
            elif data_type == "sip":
                return Literal("sip", 0.0)
            elif data_type == "flag":
                return Literal("flag", False)  # down = False
            else:
                # For unknown types, return None
                return None
    
    def _create_default_table_value(self, table_type_info: TypeInfo):
        """Create default table value with all fields initialized to their defaults"""
        if not table_type_info or not table_type_info.table_fields:
            return None
        
        field_inits = []
        for field_name, field_type in table_type_info.table_fields.items():
            default_value = self._create_default_value(field_type.base_type, field_type.dimensions)
            if default_value:
                # TableLiteral expects 4-tuple: (field_name, value, line, col)
                field_inits.append((field_name, default_value, None, None))
        
        if field_inits:
            return TableLiteral(field_inits)
        return None
        self.built = False
        self._register_builtin_recipes()
    
    def _register_builtin_recipes(self):
        """Register all built-in recipes with their overloads"""
        for recipe_name, signatures in BUILTIN_RECIPES.items():
            for signature in signatures:
                # Create mock parameter nodes for signature matching
                params = [_BuiltinParam(spice_type, spice_dims) 
                         for spice_type, spice_dims in signature.spices]
                
                # Create a mock declaration node
                declaration = _BuiltinDeclaration(
                    params, 
                    signature.return_type, 
                    signature.return_dims
                )
                
                # Create type info with is_function flag
                type_info = signature.get_return_type_info()
                type_info.is_function = True
                
                # Create symbol
                symbol = Symbol(
                    recipe_name, 
                    SymbolKind.FUNCTION, 
                    type_info, 
                    0,
                    declaration,
                    self.symbol_table.global_scope
                )
                
                # Register as built-in (allows overloading)
                self.symbol_table.register_builtin_recipe(recipe_name, symbol)
    
    def build(self, ast_root: Program) -> SymbolTable:
        """Build symbol table from AST"""
        if not isinstance(ast_root, Program):
            if self.symbol_table.error_handler:
                self.symbol_table.error_handler.add_error("Root must be a Program node")
            return self.symbol_table
        
        self._gather_type_definitions(ast_root)
        self._process_global_declarations(ast_root)
        self._process_function_declarations(ast_root)
        
        if ast_root.start_platter:
            self.symbol_table.enter_scope("start_platter")
            self._process_platter(ast_root.start_platter)
            self.symbol_table.exit_scope()
        
        self.built = True
        return self.symbol_table
    
    def _gather_type_definitions(self, program: Program):
        """Gather all table type definitions"""
        for decl in program.global_decl:
            if isinstance(decl, TablePrototype):
                self._process_table_prototype(decl)
    
    def _process_table_prototype(self, node: TablePrototype):
        """Process a table type definition"""
        field_types = {}
        seen_fields = set()
        
        for field in node.fields:
            # Check for duplicate field names
            if field.identifier in seen_fields:
                if self.symbol_table.error_handler:
                    self.symbol_table.error_handler.add_error(
                        f"Duplicate field '{field.identifier}' in table prototype '{node.name}'",
                        field,
                        "E205"
                    )
                continue
            seen_fields.add(field.identifier)
            
            dims = field.dimensions if field.dimensions is not None else 0
            field_type_info = self._create_type_info(field.data_type, dims)
            
            # Check for recursive type (field type is same as table being defined)
            if field.data_type == node.name:
                if self.symbol_table.error_handler:
                    self.symbol_table.error_handler.add_error(
                        f"Recursive type not allowed: table prototype '{node.name}' cannot contain field of type '{field.data_type}'",
                        field,
                        "E206"
                    )
                continue
            
            # Check for forward reference (table type not yet defined)
            # Only check if it's a table type (not primitive)
            if field.data_type not in ["piece", "sip", "chars", "flag"]:
                if not self.symbol_table.lookup_table_type(field.data_type):
                    if self.symbol_table.error_handler:
                        self.symbol_table.error_handler.add_error(
                            f"Forward reference not allowed: table prototype '{field.data_type}' must be defined before use in '{node.name}'",
                            field,
                            "E207"
                        )
                    continue
            
            field_types[field.identifier] = field_type_info
        
        table_type_info = TypeInfo(node.name, 0, field_types)
        
        self.symbol_table.define_symbol(
            node.name,
            SymbolKind.TABLE_TYPE,
            table_type_info,
            node
        )
    
    def _process_global_declarations(self, program: Program):
        """Process global variable declarations"""
        for decl in program.global_decl:
            if isinstance(decl, IngrDecl):
                self._process_var_decl(decl)
            elif isinstance(decl, ArrayDecl):
                self._process_array_decl(decl)
            elif isinstance(decl, TableDecl):
                self._process_table_decl(decl)
    
    def _process_function_declarations(self, program: Program):
        """Process function declarations"""
        for recipe in program.recipe_decl:
            self._process_recipe_decl(recipe)
    
    def _process_recipe_decl(self, node: RecipeDecl):
        """Process a recipe declaration"""
        # Prevent user-defined recipes from shadowing built-ins
        if self.symbol_table.is_builtin_recipe(node.name):
            if self.symbol_table.error_handler:
                self.symbol_table.error_handler.add_error(
                    f"Cannot redefine built-in recipe '{node.name}'", 
                    node
                )
            return
        
        dims = node.return_dims if node.return_dims is not None else 0
        serve_type = self._create_type_info(node.return_type, dims)
        
        recipe_symbol = Symbol(
            node.name,
            SymbolKind.FUNCTION,
            serve_type,
            0,
            node,
            self.symbol_table.current_scope
        )
        
        if not self.symbol_table.current_scope.define(recipe_symbol):
            if self.symbol_table.error_handler:
                self.symbol_table.error_handler.add_error(f"Recipe '{node.name}' already defined", node)
            return
        
        self.symbol_table.enter_scope(f"recipe_{node.name}")
        self.symbol_table.current_function = recipe_symbol
        
        for spice in node.params:
            self._process_param_decl(spice)
        
        if node.body:
            self._process_platter(node.body)
        
        self.symbol_table.current_function = None
        self.symbol_table.exit_scope()
    
    def _process_param_decl(self, node: ParamDecl):
        """Process a recipe spice (parameter)"""
        dims = node.dimensions if node.dimensions is not None else 0
        type_info = self._create_type_info(node.data_type, dims)
        
        self.symbol_table.define_symbol(
            node.identifier,
            SymbolKind.PARAMETER,
            type_info,
            node
        )
    
    def _process_var_decl(self, node: IngrDecl):
        """Process an ingredient declaration"""
        type_info = self._create_type_info(node.data_type, 0)
        
        # Add default value if not initialized
        if not node.init_value:
            node.init_value = self._create_default_value(node.data_type, 0)
        
        self.symbol_table.define_symbol(
            node.identifier,
            SymbolKind.VARIABLE,
            type_info,
            node
        )
        
        # Track usage in initial value if present
        if node.init_value:
            self._track_expression_usage(node.init_value)
    
    def _process_array_decl(self, node: ArrayDecl):
        """Process an array declaration"""
        dims = node.dimensions if node.dimensions is not None else 0
        type_info = self._create_type_info(node.data_type, dims)
        
        # Add default value if not initialized
        if not node.init_value:
            node.init_value = self._create_default_value(node.data_type, dims)
        
        self.symbol_table.define_symbol(
            node.identifier,
            SymbolKind.VARIABLE,
            type_info,
            node
        )
        
        # Track usage in initial value if present
        if node.init_value:
            self._track_expression_usage(node.init_value)
    
    def _process_table_decl(self, node: TableDecl):
        """Process a table instance declaration"""
        table_type = self.symbol_table.lookup_table_type(node.table_type)
        
        dims = node.dimensions if node.dimensions is not None else 0
        
        if table_type:
            type_info = TypeInfo(
                node.table_type,
                dims,
                table_type.table_fields if dims == 0 else None
            )
            
            if dims > 0:
                type_info.is_table = True
                type_info.table_fields = table_type.table_fields
            
            # Add default value if not initialized (only for non-array table instances)
            if not node.init_value and dims == 0:
                node.init_value = self._create_default_table_value(table_type)
        else:
            type_info = TypeInfo(node.table_type, dims)
        
        self.symbol_table.define_symbol(
            node.identifier,
            SymbolKind.VARIABLE,
            type_info,
            node
        )
        
        # Track usage in initial value if present
        if node.init_value:
            self._track_expression_usage(node.init_value)
    
    def _process_platter(self, node: Platter):
        """Process a block/compound statement"""
        for decl in node.local_decls:
            if isinstance(decl, IngrDecl):
                self._process_var_decl(decl)
            elif isinstance(decl, ArrayDecl):
                self._process_array_decl(decl)
            elif isinstance(decl, TableDecl):
                self._process_table_decl(decl)
        
        for stmt in node.statements:
            self._process_statement(stmt)
    
    def _process_statement(self, node: ASTNode):
        """Process a statement"""
        if isinstance(node, CheckStatement):
            self._process_if_statement(node)
        elif isinstance(node, MenuStatement):
            self._process_switch_statement(node)
        elif isinstance(node, RepeatLoop):
            self._process_while_loop(node)
        elif isinstance(node, OrderRepeatLoop):
            self._process_do_while_loop(node)
        elif isinstance(node, PassLoop):
            self._process_for_loop(node)
        elif isinstance(node, Platter):
            self.symbol_table.enter_scope("block")
            self._process_platter(node)
            self.symbol_table.exit_scope()
        elif isinstance(node, Assignment):
            self._track_expression_usage(node.target)
            self._track_expression_usage(node.value)
        elif isinstance(node, ServeStatement):
            if node.value:
                self._track_expression_usage(node.value)
        elif isinstance(node, ExpressionStatement):
            self._track_expression_usage(node.expr)
    
    def _process_if_statement(self, node: CheckStatement):
        """Process if statement - use Platter syntax: check/alt/instead"""
        # Track condition expression usage
        self._track_expression_usage(node.condition)
        
        self.symbol_table.enter_scope("check")
        self._process_platter(node.then_block)
        self.symbol_table.exit_scope()
        
        for i, (elif_cond, elif_block) in enumerate(node.elif_clauses):
            self._track_expression_usage(elif_cond)
            self.symbol_table.enter_scope("alt")
            self._process_platter(elif_block)
            self.symbol_table.exit_scope()
        
        if node.else_block:
            self.symbol_table.enter_scope("instead")
            self._process_platter(node.else_block)
            self.symbol_table.exit_scope()
    
    def _process_switch_statement(self, node: MenuStatement):
        """Process menu statement - use Platter syntax: menu/choice/usual"""
        # Track menu expression usage
        self._track_expression_usage(node.expr)
        
        for i, case in enumerate(node.cases):
            self.symbol_table.enter_scope("choice")
            for stmt in case.statements:
                self._process_statement(stmt)
            self.symbol_table.exit_scope()
        
        if node.default:
            self.symbol_table.enter_scope("usual")
            for stmt in node.default:
                self._process_statement(stmt)
            self.symbol_table.exit_scope()
    
    def _process_while_loop(self, node: RepeatLoop):
        """Process while loop - use Platter syntax: repeat"""
        self.symbol_table.in_loop += 1
        # Track condition expression usage
        self._track_expression_usage(node.condition)
        
        self.symbol_table.enter_scope("repeat")
        self._process_platter(node.body)
        self.symbol_table.exit_scope()
        self.symbol_table.in_loop -= 1
    
    def _process_do_while_loop(self, node: OrderRepeatLoop):
        """Process do-while loop - use Platter syntax: order_repeat"""
        self.symbol_table.in_loop += 1
        self.symbol_table.enter_scope("order_repeat")
        self._process_platter(node.body)
        self.symbol_table.exit_scope()
        # Track condition expression usage
        self._track_expression_usage(node.condition)
        self.symbol_table.in_loop -= 1
    
    def _process_for_loop(self, node: PassLoop):
        """Process for loop - use Platter syntax: pass"""
        self.symbol_table.in_loop += 1
        
        # Enter scope for the entire for loop
        self.symbol_table.enter_scope("pass")
        
        # Track init, condition, and update expressions (treat as usage, not declaration)
        if node.init and isinstance(node.init, Assignment):
            self._track_expression_usage(node.init.target)
            self._track_expression_usage(node.init.value)
        
        if node.condition:
            self._track_expression_usage(node.condition)
            
        if node.update:
            if isinstance(node.update, Assignment):
                self._track_expression_usage(node.update.target)
                self._track_expression_usage(node.update.value)
        
        # Process loop body
        self._process_platter(node.body)
        
        self.symbol_table.exit_scope()
        self.symbol_table.in_loop -= 1
    
    def _create_type_info(self, base_type: str, dimensions: int = 0) -> TypeInfo:
        """Create TypeInfo"""
        dims = dimensions if dimensions is not None else 0
        
        table_type = self.symbol_table.lookup_table_type(base_type)
        if table_type:
            return TypeInfo(base_type, dims, table_type.table_fields)
        
        return TypeInfo(base_type, dims)
    
    def _track_expression_usage(self, expr: ASTNode):
        """Track symbol usage in expressions"""
        if expr is None:
            return
        
        if isinstance(expr, Identifier):
            # Look up the symbol and record usage
            symbol = self.symbol_table.lookup_symbol(expr.name)
            if symbol:  # Find the scope where this symbol is declared
                declared_scope = self._find_declaring_scope(symbol.name)
                if declared_scope:
                    # Record usage with both current scope and declaring scope
                    symbol.add_usage(self.symbol_table.current_scope.name, declared_scope.name)
            else:
                # Symbol not declared - track as undeclared but accessed
                if expr.name not in self.symbol_table.undeclared_symbols:
                    # Create a phantom symbol with no declaration
                    undeclared_symbol = Symbol(
                        name=expr.name,
                        kind=SymbolKind.VARIABLE,  # Assume variable
                        type_info=TypeInfo("unknown", 0),
                        scope_level=-1,  # Special marker for undeclared
                        declaration_node=None,
                        declared_scope=None  # No declaration scope
                    )
                    self.symbol_table.undeclared_symbols[expr.name] = undeclared_symbol
                else:
                    undeclared_symbol = self.symbol_table.undeclared_symbols[expr.name]
                
                # Track where it was accessed (avoid duplicates)
                current_scope_name = self.symbol_table.current_scope.name
                if current_scope_name not in undeclared_symbol.accessed_in_scopes:
                    undeclared_symbol.accessed_in_scopes.append(current_scope_name)
        
        elif isinstance(expr, BinaryOp):
            self._track_expression_usage(expr.left)
            self._track_expression_usage(expr.right)
        
        elif isinstance(expr, UnaryOp):
            self._track_expression_usage(expr.operand)
        
        elif isinstance(expr, ArrayAccess):
            self._track_expression_usage(expr.array)
            self._track_expression_usage(expr.index)
        
        elif isinstance(expr, TableAccess):
            self._track_expression_usage(expr.table)
        
        elif isinstance(expr, RecipeCall):
            # Track recipe name usage
            symbol = self.symbol_table.lookup_symbol(expr.name)
            if symbol:
                declared_scope = self._find_declaring_scope(symbol.name)
                if declared_scope:
                    symbol.add_usage(self.symbol_table.current_scope.name, declared_scope.name)
            else:
                # Recipe not declared - track as undeclared but accessed
                if expr.name not in self.symbol_table.undeclared_symbols:
                    undeclared_symbol = Symbol(
                        name=expr.name,
                        kind=SymbolKind.FUNCTION,
                        type_info=TypeInfo("unknown", 0),
                        scope_level=-1,
                        declaration_node=None,
                        declared_scope=None
                    )
                    self.symbol_table.undeclared_symbols[expr.name] = undeclared_symbol
                else:
                    undeclared_symbol = self.symbol_table.undeclared_symbols[expr.name]
                
                # Track where it was accessed (avoid duplicates)
                current_scope_name = self.symbol_table.current_scope.name
                if current_scope_name not in undeclared_symbol.accessed_in_scopes:
                    undeclared_symbol.accessed_in_scopes.append(current_scope_name)
            # Track flavors (arguments)
            for arg in expr.args:
                self._track_expression_usage(arg)
        
        elif isinstance(expr, CastExpr):
            self._track_expression_usage(expr.expr)
        
        elif isinstance(expr, ArrayLiteral):
            for elem in expr.elements:
                self._track_expression_usage(elem)
        
        elif isinstance(expr, TableLiteral):
            for field_name, value, line, col in expr.field_inits:
                self._track_expression_usage(value)
    
    def _find_declaring_scope(self, symbol_name: str) -> Optional[Scope]:
        """Find the scope where a symbol is declared"""
        scope = self.symbol_table.current_scope
        while scope:
            if symbol_name in scope.symbols:
                return scope
            scope = scope.parent
        return None


# Helper Functions
def build_symbol_table(ast_root: Program) -> SymbolTable:
    """Build symbol table from AST"""
    builder = SymbolTableBuilder()
    return builder.build(ast_root)


def print_symbol_table(symbol_table: SymbolTable, error_handler=None):
    """Print symbol table in formatted table layout"""
    from app.semantic_analyzer.symbol_table.symbol_table_output import format_symbol_table_compact
    
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 25 + "SYMBOL TABLE ANALYSIS" + " " * 32 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    formatted_output = format_symbol_table_compact(symbol_table, error_handler)
    print(formatted_output)
