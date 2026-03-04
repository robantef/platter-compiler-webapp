# Complete AST Nodes for Platter Language

# Base node
class ASTNode:
    def __init__(self, node_type="ASTNode", line=None, column=None): 
        self.node_type = node_type
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"

# ============================================================================
# Program Structure
# ============================================================================

class Program(ASTNode):
    """Root node of the AST"""
    def __init__(self, line=None, column=None): 
        super().__init__("Program", line, column)
        self.global_decl = []  # List of declaration nodes
        self.recipe_decl = []  # List of RecipeDecl nodes
        self.start_platter = None  # Platter node
    
    def add_global_decl(self, node): 
        if node:
            self.global_decl.append(node)
        
    def add_recipe_decl(self, node): 
        if node:
            self.recipe_decl.append(node)

    def set_start_platter(self, node): 
        self.start_platter = node
    
    def __repr__(self):
        return f"Program(global_decl={len(self.global_decl)}, recipe_decl={len(self.recipe_decl)}, start_platter={'Yes' if self.start_platter else 'No'})"

# ============================================================================
# Declarations
# ============================================================================

class IngrDecl(ASTNode):
    """Ingredient declaration (scalar ingredient)"""
    def __init__(self, data_type, identifier, init_value=None, line=None, column=None):
        super().__init__("IngrDecl", line, column)
        self.data_type = data_type  # "piece", "sip", "flag", "chars"
        self.identifier = identifier  # String
        self.init_value = init_value  # Expression node or None
    
    def __repr__(self):
        return f"IngrDecl({self.data_type} {self.identifier}, init={'Yes' if self.init_value else 'No'})"

class ArrayDecl(ASTNode):
    """Array declaration"""
    def __init__(self, data_type, dimensions, identifier, init_value=None, line=None, column=None):
        super().__init__("ArrayDecl", line, column)
        self.data_type = data_type
        self.dimensions = dimensions  # int: number of dimensions
        self.identifier = identifier
        self.init_value = init_value  # ArrayLiteral or Expression
    
    def __repr__(self):
        return f"ArrayDecl({self.data_type}[{self.dimensions}] {self.identifier})"

class TablePrototype(ASTNode):
    """Table type definition"""
    def __init__(self, name, fields, line=None, column=None):
        super().__init__("TablePrototype", line, column)
        self.name = name
        self.fields = fields  # List of FieldDecl nodes
    
    def __repr__(self):
        return f"TablePrototype({self.name}, {len(self.fields)} fields)"

class FieldDecl(ASTNode):
    """Field in a table prototype"""
    def __init__(self, data_type, dimensions, identifier, line=None, column=None):
        super().__init__("FieldDecl", line, column)
        self.data_type = data_type  # "piece", "sip", "flag", "chars", or table name
        self.dimensions = dimensions  # int
        self.identifier = identifier
    
    def __repr__(self):
        dims = f"[{self.dimensions}]" if self.dimensions > 0 else ""
        return f"FieldDecl({self.data_type}{dims} {self.identifier})"

class TableDecl(ASTNode):
    """Table instance declaration"""
    def __init__(self, table_type, identifier, init_value=None, dimensions=0, line=None, column=None):
        super().__init__("TableDecl", line, column)
        self.table_type = table_type  # String: name of table type
        self.identifier = identifier
        self.init_value = init_value  # TableLiteral or None
        self.dimensions = dimensions
    
    def __repr__(self):
        dims = f"[{self.dimensions}]" if self.dimensions > 0 else ""
        return f"TableDecl({self.table_type}{dims} {self.identifier})"

class RecipeDecl(ASTNode):
    """Recipe declaration (prepare)"""
    def __init__(self, return_type, return_dims, name, params, body, line=None, column=None):
        super().__init__("RecipeDecl", line, column)
        self.return_type = return_type
        self.return_dims = return_dims  # int
        self.name = name
        self.params = params  # List of ParamDecl nodes (spices)
        self.body = body  # Platter node
    
    def __repr__(self):
        dims = f"[{self.return_dims}]" if self.return_dims > 0 else ""
        return f"RecipeDecl({self.return_type}{dims} {self.name}({len(self.params)} spices))"

class ParamDecl(ASTNode):
    """Recipe spice (parameter)"""
    def __init__(self, data_type, dimensions, identifier, line=None, column=None):
        super().__init__("ParamDecl", line, column)
        self.data_type = data_type
        self.dimensions = dimensions
        self.identifier = identifier
    
    def __repr__(self):
        dims = f"[{self.dimensions}]" if self.dimensions > 0 else ""
        return f"ParamDecl({self.data_type}{dims} {self.identifier})"

# ============================================================================
# Statements
# ============================================================================

class Platter(ASTNode):
    """Block/compound statement"""
    def __init__(self, local_decls=None, statements=None, line=None, column=None):
        super().__init__("Platter", line, column)
        self.local_decls = local_decls or []
        self.statements = statements or []
    
    def add_local_decl(self, node):
        if node:
            self.local_decls.append(node)
    
    def add_statement(self, node):
        if node:
            self.statements.append(node)
    
    def __repr__(self):
        return f"Platter(decls={len(self.local_decls)}, stmts={len(self.statements)})"

class Assignment(ASTNode):
    """Assignment statement"""
    def __init__(self, target, operator, value, line=None, column=None):
        super().__init__("Assignment", line, column)
        self.target = target  # Identifier or accessor node
        self.operator = operator  # "=", "+=", "-=", "*=", "/=", "%="
        self.value = value  # Expression node
    
    def __repr__(self):
        return f"Assignment({self.operator})"

class CheckStatement(ASTNode):
    """Conditional statement (check/alt/instead)"""
    def __init__(self, condition, then_block, elif_clauses=None, else_block=None, line=None, column=None):
        super().__init__("CheckStatement", line, column)
        self.condition = condition  # Expression
        self.then_block = then_block  # Platter
        self.elif_clauses = elif_clauses or []  # List of (condition, block) tuples (alt)
        self.else_block = else_block  # Platter or None (instead)
    
    def add_elif(self, condition, block):
        self.elif_clauses.append((condition, block))
    
    def __repr__(self):
        return f"CheckStatement(alts={len(self.elif_clauses)}, instead={'Yes' if self.else_block else 'No'})"

class MenuStatement(ASTNode):
    """Menu statement (menu/choice/usual)"""
    def __init__(self, expr, cases, default=None, line=None, column=None):
        super().__init__("MenuStatement", line, column)
        self.expr = expr  # Expression to menu on
        self.cases = cases or []  # List of CaseClause nodes (choice)
        self.default = default  # Statements list or None (usual)
    
    def add_case(self, case_node):
        self.cases.append(case_node)
    
    def __repr__(self):
        return f"MenuStatement({len(self.cases)} choices, usual={'Yes' if self.default else 'No'})"

class CaseClause(ASTNode):
    """Choice in a menu statement"""
    def __init__(self, value, statements, line=None, column=None):
        super().__init__("CaseClause", line, column)
        self.value = value  # Literal value
        self.statements = statements  # List of statement nodes
    
    def __repr__(self):
        return f"CaseClause({len(self.statements)} stmts)"

class RepeatLoop(ASTNode):
    """Repeat loop (repeat)"""
    def __init__(self, condition, body, line=None, column=None):
        super().__init__("RepeatLoop", line, column)
        self.condition = condition
        self.body = body  # Platter
    
    def __repr__(self):
        return f"RepeatLoop()"

class OrderRepeatLoop(ASTNode):
    """Order-repeat loop (order...repeat)"""
    def __init__(self, body, condition, line=None, column=None):
        super().__init__("OrderRepeatLoop", line, column)
        self.body = body
        self.condition = condition
    
    def __repr__(self):
        return f"OrderRepeatLoop()"

class PassLoop(ASTNode):
    """Pass loop (pass)"""
    def __init__(self, init, update, condition, body, line=None, column=None):
        super().__init__("PassLoop", line, column)
        self.init = init  # Assignment or None
        self.update = update  # Assignment
        self.condition = condition  # Expression
        self.body = body  # Platter
    
    def __repr__(self):
        return f"PassLoop()"

class ServeStatement(ASTNode):
    """Serve statement (serve)"""
    def __init__(self, value=None, line=None, column=None):
        super().__init__("ServeStatement", line, column)
        self.value = value  # Expression or None
    
    def __repr__(self):
        return f"ServeStatement(has_value={'Yes' if self.value else 'No'})"

class BreakStatement(ASTNode):
    """Stop statement (stop)"""
    def __init__(self, line=None, column=None):
        super().__init__("BreakStatement", line, column)
    
    def __repr__(self):
        return "BreakStatement()"

class ContinueStatement(ASTNode):
    """Next statement (next)"""
    def __init__(self, line=None, column=None):
        super().__init__("ContinueStatement", line, column)
    
    def __repr__(self):
        return "ContinueStatement()"

class ExpressionStatement(ASTNode):
    """Expression used as statement"""
    def __init__(self, expr, line=None, column=None):
        super().__init__("ExpressionStatement", line, column)
        self.expr = expr
    
    def __repr__(self):
        return f"ExpressionStatement({self.expr})"

# ============================================================================
# Expressions
# ============================================================================

class BinaryOp(ASTNode):
    """Binary operation"""
    def __init__(self, left, operator, right, line=None, column=None):
        super().__init__("BinaryOp", line, column)
        self.left = left
        self.operator = operator  # "+", "-", "*", "/", "%", "==", "!=", ">", "<", ">=", "<=", "and", "or"
        self.right = right
        
        # Auto-rotate tree to fix right-associativity issues from LL(1) grammar
        precedence = {
            "or": 0, "and": 1, 
            "==": 2, "!=": 2,
            "<": 3, ">": 3, "<=": 3, ">=": 3,
            "+": 4, "-": 4,
            "*": 5, "/": 5, "%": 5
        }
        
        while isinstance(self.right, BinaryOp):
            my_prec = precedence.get(self.operator, -1)
            right_prec = precedence.get(self.right.operator, -1)
            
            # If our operator binds tighter than or equal to the right operator, rotate left!
            if my_prec >= right_prec and right_prec != -1:
                # new left child is our original operator with the right's left child
                new_left = BinaryOp(self.left, self.operator, self.right.left, self.line, self.column)
                
                # We become the right operator's identity
                self.operator = self.right.operator
                self.left = new_left
                self.right = self.right.right
            else:
                break
    
    def __repr__(self):
        return f"BinaryOp({self.operator})"

class UnaryOp(ASTNode):
    """Unary operation"""
    def __init__(self, operator, operand, line=None, column=None):
        super().__init__("UnaryOp", line, column)
        self.operator = operator  # "not", "-"
        self.operand = operand
    
    def __repr__(self):
        return f"UnaryOp({self.operator})"

class Identifier(ASTNode):
    """Ingredient reference"""
    def __init__(self, name, line=None, column=None):
        super().__init__("Identifier", line, column)
        self.name = name
    
    def __repr__(self):
        return f"Identifier({self.name})"

class ArrayAccess(ASTNode):
    """Array element access"""
    def __init__(self, array, index, line=None, column=None):
        super().__init__("ArrayAccess", line, column)
        self.array = array  # Expression
        self.index = index  # Expression
    
    def __repr__(self):
        return f"ArrayAccess()"

class TableAccess(ASTNode):
    """Table field access"""
    def __init__(self, table, field, line=None, column=None):
        super().__init__("TableAccess", line, column)
        self.table = table  # Expression
        self.field = field  # String
    
    def __repr__(self):
        return f"TableAccess(.{self.field})"

class RecipeCall(ASTNode):
    """Recipe call"""
    def __init__(self, name, args=None, line=None, column=None):
        super().__init__("RecipeCall", line, column)
        self.name = name
        self.args = args or []  # flavors
    
    def add_arg(self, arg):
        self.args.append(arg)
    
    def __repr__(self):
        return f"RecipeCall({self.name}, {len(self.args)} flavors)"

class CastExpr(ASTNode):
    """Type cast expression"""
    def __init__(self, target_type, expr, line=None, column=None):
        super().__init__("CastExpr", line, column)
        self.target_type = target_type  # "piece", "sip", "flag", "chars"
        self.expr = expr
    
    def __repr__(self):
        return f"CastExpr(to{self.target_type})"

# ============================================================================
# Literals
# ============================================================================

class Literal(ASTNode):
    """Literal value (piece/sip/flag/chars)"""
    def __init__(self, value_type, value, line=None, column=None):
        super().__init__("Literal", line, column)
        self.value_type = value_type  # "piece", "sip", "flag", "chars"
        self.value = value
    
    def __repr__(self):
        # Display 'up' for True and 'down' for False in repr
        if self.value_type == "flag":
            display_val = "up" if self.value else "down"
            return f"Literal({self.value_type}: {display_val})"
        return f"Literal({self.value_type}: {self.value})"

class ArrayLiteral(ASTNode):
    """Array literal"""
    def __init__(self, elements=None, line=None, column=None):
        super().__init__("ArrayLiteral", line, column)
        self.elements = elements or []
    
    def add_element(self, elem):
        if elem:
            self.elements.append(elem)
    
    def __repr__(self):
        return f"ArrayLiteral([{len(self.elements)}])"

class TableLiteral(ASTNode):
    """Table literal"""
    def __init__(self, field_inits=None, line=None, column=None):
        super().__init__("TableLiteral", line, column)
        self.field_inits = field_inits or []  # List of (field_name, value, line, col) tuples
    
    def add_field(self, field_name, value):
        self.field_inits.append((field_name, value))
    
    def __repr__(self):
        return f"TableLiteral({len(self.field_inits)} fields)"