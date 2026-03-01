"""
Auto-generated AST-building parser. Do not edit by hand.
Generated from cfg.tsv and ast.tsv
"""

from app.lexer.token import Token
from app.parser.error_handler import ErrorHandler
from app.parser.predict_set import PREDICT_SET
from app.parser.first_set import FIRST_SET
from app.semantic_analyzer.ast.ast_nodes import *
import logging as log

log.basicConfig(level=log.DEBUG, format='%(levelname)s: <%(funcName)s> | %(message)s')


class ASTParser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type not in ("space", "tab", "newline", "comment_single", "comment_multi")]
        self.error_arr = []
        
        # Context variables for passing info to tail parsing functions
        self._context_dimensions = None
        self._context_type = None
        self._context_identifier = None  # For passing identifier names to function calls
        self._context_identifier_line = None
        self._context_identifier_col = None
        
        if not self.tokens:
            raise ErrorHandler("EOF", None, PREDICT_SET["<program>"])
        
        last_token = self.tokens[-1]
        self.tokens.append(Token("EOF", "EOF", last_token.line, last_token.col))
        
        self.pos = 0
    
    def parse_token(self, tok):
        """Parse and consume a specific token type"""
        if self.pos >= len(self.tokens):
            raise ErrorHandler("EOF", None, tok)
        
        if self.tokens[self.pos].type == tok:
            log.warning(f"Expected: {tok} | Current: {self.tokens[self.pos].type} | Remark: MATCH!")
            self.pos += 1
            self.error_arr.clear()
        else:
            log.warning(f"Expected: {tok} | Current: {self.tokens[self.pos].type} | Remark: INVALID!\n")
            
            if tok != self.error_arr:
                if isinstance(tok, list):
                    self.error_arr.extend([t for t in tok if t not in self.error_arr])
                else:
                    if tok not in self.error_arr:
                        self.error_arr.append(tok)
            
            log.info("STACK: " + str(self.error_arr) + "\n")
            self.error_arr = list(dict.fromkeys(self.error_arr))
            raise ErrorHandler("Unexpected_err", self.tokens[self.pos], self.error_arr)
    
    def appendF(self, first_set):
        first_set = [t for t in first_set if not (t=="λ")]
        self.error_arr.extend(first_set)
    
    def parse_program(self):
        """Entry point for parsing"""
        self.appendF(FIRST_SET["<program>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    1 <program>	=>	<global_decl>	<recipe_decl>	start	(	)	<platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<program>"]:
            node_0 = self.global_decl()
            node_1 = self.recipe_decl()
            token_2 = self.tokens[self.pos]
            self.parse_token("start")
            token_3 = self.tokens[self.pos]
            self.parse_token("(")
            token_4 = self.tokens[self.pos]
            self.parse_token(")")
            node_5 = self.platter()
            
            # Create Program node
            prog = Program()
            if isinstance(node_0, list):
                for decl in node_0:
                    prog.add_global_decl(decl)
            if isinstance(node_1, list):
                for recipe in node_1:
                    prog.add_recipe_decl(recipe)
            prog.set_start_platter(node_5)
            
            # Ensure we've consumed all tokens
            if self.pos < len(self.tokens) and self.tokens[self.pos].type != "EOF":
                raise ErrorHandler("ExpectedEOF_err", self.tokens[self.pos], None)
            
            log.info("Exit: " + self.tokens[self.pos].type)
            return prog
        else:
            self.parse_token(self.error_arr)



    def global_decl(self):
        self.appendF(FIRST_SET["<global_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    2 <global_decl>	=>	piece	<piece_decl>	<global_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<global_decl>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("piece")
            node_1 = self.piece_decl()
            node_2 = self.global_decl()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    3 <global_decl>	=>	chars	<chars_decl>	<global_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("chars")
            node_1 = self.chars_decl()
            node_2 = self.global_decl()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    4 <global_decl>	=>	sip	<sip_decl>	<global_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("sip")
            node_1 = self.sip_decl()
            node_2 = self.global_decl()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    5 <global_decl>	=>	flag	<flag_decl>	<global_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("flag")
            node_1 = self.flag_decl()
            node_2 = self.global_decl()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    6 <global_decl>	=>	<table_prototype>	<global_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_4"]:
            node_0 = self.table_prototype()
            node_1 = self.global_decl()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    7 <global_decl>	=>	id	<table_decl>	<global_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_5"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            # Set table type context
            self._context_type = token_0.value
            node_1 = self.table_decl()
            node_2 = self.global_decl()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    8 <global_decl>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<global_decl>_6"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def piece_decl(self):
        self.appendF(FIRST_SET["<piece_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    9 <piece_decl>	=>	of	<piece_id>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_decl>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("of")
            node_1 = self.piece_id()
            token_2 = self.tokens[self.pos]
            self.parse_token(";")

            return node_1

            """    10 <piece_decl>	=>	<piece_array_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_decl>_1"]:
            node_0 = self.piece_array_decl()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def piece_id(self):
        self.appendF(FIRST_SET["<piece_id>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    11 <piece_id>	=>	id	<piece_ingredient_init>	<piece_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_id>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.piece_ingredient_init()
            node_2 = self.piece_id_tail()

            # Collect: [IngrDecl("piece", $0.value, $1)] + $2
            result = [IngrDecl("piece", token_0.value, node_1, token_0.line, token_0.col)] + node_2
            return result
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def piece_ingredient_init(self):
        self.appendF(FIRST_SET["<piece_ingredient_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    12 <piece_ingredient_init>	=>	=	<strict_piece_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_ingredient_init>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("=")
            node_1 = self.strict_piece_expr()

            return node_1

            """    13 <piece_ingredient_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_ingredient_init>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def piece_id_tail(self):
        self.appendF(FIRST_SET["<piece_id_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    14 <piece_id_tail>	=>	,	id	<piece_ingredient_init>	<piece_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_id_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            token_1 = self.tokens[self.pos]
            self.parse_token("id")
            node_2 = self.piece_ingredient_init()
            node_3 = self.piece_id_tail()

            # Collect: [IngrDecl("piece", $1.value, $2)] + $3
            result = [IngrDecl("piece", token_1.value, node_2, token_1.line, token_1.col)] + node_3
            return result

            """    15 <piece_id_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_id_tail>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def chars_decl(self):
        self.appendF(FIRST_SET["<chars_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    16 <chars_decl>	=>	of	<chars_id>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_decl>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("of")
            node_1 = self.chars_id()
            token_2 = self.tokens[self.pos]
            self.parse_token(";")

            return node_1

            """    17 <chars_decl>	=>	<chars_array_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_decl>_1"]:
            node_0 = self.chars_array_decl()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def chars_id(self):
        self.appendF(FIRST_SET["<chars_id>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    18 <chars_id>	=>	id	<chars_ingredient_init>	<chars_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_id>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.chars_ingredient_init()
            node_2 = self.chars_id_tail()

            # Collect: [IngrDecl("chars", $0.value, $1)] + $2
            result = [IngrDecl("chars", token_0.value, node_1, token_0.line, token_0.col)] + node_2
            return result
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def chars_ingredient_init(self):
        self.appendF(FIRST_SET["<chars_ingredient_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    19 <chars_ingredient_init>	=>	=	<strict_chars_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_ingredient_init>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("=")
            node_1 = self.strict_chars_expr()

            return node_1

            """    20 <chars_ingredient_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_ingredient_init>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def chars_id_tail(self):
        self.appendF(FIRST_SET["<chars_id_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    21 <chars_id_tail>	=>	,	id	<chars_ingredient_init>	<chars_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_id_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            token_1 = self.tokens[self.pos]
            self.parse_token("id")
            node_2 = self.chars_ingredient_init()
            node_3 = self.chars_id_tail()

            # Collect: [IngrDecl("chars", $1.value, $2)] + $3
            result = [IngrDecl("chars", token_1.value, node_2, token_1.line, token_1.col)] + node_3
            return result

            """    22 <chars_id_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_id_tail>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def sip_decl(self):
        self.appendF(FIRST_SET["<sip_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    23 <sip_decl>	=>	of	<sip_id>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_decl>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("of")
            node_1 = self.sip_id()
            token_2 = self.tokens[self.pos]
            self.parse_token(";")

            return node_1

            """    24 <sip_decl>	=>	<sip_array_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_decl>_1"]:
            node_0 = self.sip_array_decl()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def sip_id(self):
        self.appendF(FIRST_SET["<sip_id>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    25 <sip_id>	=>	id	<sip_ingredient_init>	<sip_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_id>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.sip_ingredient_init()
            node_2 = self.sip_id_tail()

            # Collect: [IngrDecl("sip", $0.value, $1)] + $2
            result = [IngrDecl("sip", token_0.value, node_1, token_0.line, token_0.col)] + node_2
            return result
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def sip_ingredient_init(self):
        self.appendF(FIRST_SET["<sip_ingredient_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    26 <sip_ingredient_init>	=>	=	<strict_sip_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_ingredient_init>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("=")
            node_1 = self.strict_sip_expr()

            return node_1

            """    27 <sip_ingredient_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_ingredient_init>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def sip_id_tail(self):
        self.appendF(FIRST_SET["<sip_id_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    28 <sip_id_tail>	=>	,	id	<sip_ingredient_init>	<sip_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_id_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            token_1 = self.tokens[self.pos]
            self.parse_token("id")
            node_2 = self.sip_ingredient_init()
            node_3 = self.sip_id_tail()

            # Collect: [IngrDecl("sip", $1.value, $2)] + $3
            result = [IngrDecl("sip", token_1.value, node_2, token_1.line, token_1.col)] + node_3
            return result

            """    29 <sip_id_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_id_tail>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_decl(self):
        self.appendF(FIRST_SET["<flag_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    30 <flag_decl>	=>	of	<flag_id>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_decl>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("of")
            node_1 = self.flag_id()
            token_2 = self.tokens[self.pos]
            self.parse_token(";")

            return node_1

            """    31 <flag_decl>	=>	<flag_array_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_decl>_1"]:
            node_0 = self.flag_array_decl()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_id(self):
        self.appendF(FIRST_SET["<flag_id>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    32 <flag_id>	=>	id	<flag_ingredient_init>	<flag_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_id>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.flag_ingredient_init()
            node_2 = self.flag_id_tail()

            # Collect: [IngrDecl("flag", $0.value, $1)] + $2
            result = [IngrDecl("flag", token_0.value, node_1, token_0.line, token_0.col)] + node_2
            return result
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_ingredient_init(self):
        self.appendF(FIRST_SET["<flag_ingredient_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    33 <flag_ingredient_init>	=>	=	<strict_flag_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_ingredient_init>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("=")
            node_1 = self.strict_flag_expr()

            return node_1

            """    34 <flag_ingredient_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_ingredient_init>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_id_tail(self):
        self.appendF(FIRST_SET["<flag_id_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    35 <flag_id_tail>	=>	,	id	<flag_ingredient_init>	<flag_id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_id_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            token_1 = self.tokens[self.pos]
            self.parse_token("id")
            node_2 = self.flag_ingredient_init()
            node_3 = self.flag_id_tail()

            # Collect: [IngrDecl("flag", $1.value, $2)] + $3
            result = [IngrDecl("flag", token_1.value, node_2, token_1.line, token_1.col)] + node_3
            return result

            """    36 <flag_id_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_id_tail>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def piece_array_decl(self):
        self.appendF(FIRST_SET["<piece_array_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    37 <piece_array_decl>	=>	<dimensions>	of	id	<piece_array_init>	<array_declare_tail_piece>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_array_decl>"]:
            node_0 = self.dimensions()
            token_1 = self.tokens[self.pos]
            self.parse_token("of")
            token_2 = self.tokens[self.pos]
            self.parse_token("id")
            node_3 = self.piece_array_init()
            # Set context for array tail declarations
            self._context_dimensions = node_0
            node_4 = self.array_declare_tail_piece()
            token_5 = self.tokens[self.pos]
            self.parse_token(";")

            # Collect: [ArrayDecl("piece",$0,$2.value,$3)] + $4
            result = [ArrayDecl("piece",node_0,token_2.value,node_3, token_2.line, token_2.col)] + node_4
            return result
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def sip_array_decl(self):
        self.appendF(FIRST_SET["<sip_array_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    38 <sip_array_decl>	=>	<dimensions>	of	id	<sip_array_init>	<array_declare_tail_sip>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_array_decl>"]:
            node_0 = self.dimensions()
            token_1 = self.tokens[self.pos]
            self.parse_token("of")
            token_2 = self.tokens[self.pos]
            self.parse_token("id")
            node_3 = self.sip_array_init()
            # Set context for array tail declarations
            self._context_dimensions = node_0
            node_4 = self.array_declare_tail_sip()
            token_5 = self.tokens[self.pos]
            self.parse_token(";")

            # Collect: [ArrayDecl("sip",$0,$2.value,$3)] + $4
            result = [ArrayDecl("sip",node_0,token_2.value,node_3, token_2.line, token_2.col)] + node_4
            return result
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def chars_array_decl(self):
        self.appendF(FIRST_SET["<chars_array_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    39 <chars_array_decl>	=>	<dimensions>	of	id	<chars_array_init>	<array_declare_tail_chars>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_array_decl>"]:
            node_0 = self.dimensions()
            token_1 = self.tokens[self.pos]
            self.parse_token("of")
            token_2 = self.tokens[self.pos]
            self.parse_token("id")
            node_3 = self.chars_array_init()
            # Set context for array tail declarations
            self._context_dimensions = node_0
            node_4 = self.array_declare_tail_chars()
            token_5 = self.tokens[self.pos]
            self.parse_token(";")

            # Collect: [ArrayDecl("chars",$0,$2.value,$3)] + $4
            result = [ArrayDecl("chars",node_0,token_2.value,node_3, token_2.line, token_2.col)] + node_4
            return result
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_array_decl(self):
        self.appendF(FIRST_SET["<flag_array_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    40 <flag_array_decl>	=>	<dimensions>	of	id	<flag_array_init>	<array_declare_tail_flag>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_array_decl>"]:
            node_0 = self.dimensions()
            token_1 = self.tokens[self.pos]
            self.parse_token("of")
            token_2 = self.tokens[self.pos]
            self.parse_token("id")
            node_3 = self.flag_array_init()
            # Set context for array tail declarations
            self._context_dimensions = node_0
            node_4 = self.array_declare_tail_flag()
            token_5 = self.tokens[self.pos]
            self.parse_token(";")

            # Collect: [ArrayDecl("flag",$0,$2.value,$3)] + $4
            result = [ArrayDecl("flag",node_0,token_2.value,node_3, token_2.line, token_2.col)] + node_4
            return result
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def table_array_decl(self):
        self.appendF(FIRST_SET["<table_array_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    41 <table_array_decl>	=>	<dimensions>	of	id	<table_array_init>	<array_declare_tail_table>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_array_decl>"]:
            node_0 = self.dimensions()
            token_1 = self.tokens[self.pos]
            self.parse_token("of")
            token_2 = self.tokens[self.pos]
            self.parse_token("id")
            node_3 = self.table_array_init()
            # Set context for array tail declarations
            self._context_dimensions = node_0
            node_4 = self.array_declare_tail_table()
            token_5 = self.tokens[self.pos]
            self.parse_token(";")

            # Collect: [ArrayDecl(CONTEXT_TYPE,$0,$2.value,$3)] + $4
            result = [ArrayDecl(self._context_type,node_0,token_2.value,node_3, token_2.line, token_2.col)] + node_4
            return result
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def piece_array_val(self):
        self.appendF(FIRST_SET["<piece_array_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    42 <piece_array_val>	=>	id	<id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_array_val>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.id_tail()

            return Identifier(token_0.value, token_0.line, token_0.col)

            """    43 <piece_array_val>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_array_val>_1"]:
            node_0 = self.ret_array()

            return node_0

            """    44 <piece_array_val>	=>	[	<array_element_piece_opt>	]    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_array_val>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.array_element_piece_opt()
            token_2 = self.tokens[self.pos]
            self.parse_token("]")

            # Create ArrayLiteral node
            node = ArrayLiteral(node_1, token_0.line, token_0.col)
            return node

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def piece_array_init(self):
        self.appendF(FIRST_SET["<piece_array_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    45 <piece_array_init>	=>	=	<piece_array_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<piece_array_init>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("=")
            node_1 = self.piece_array_val()

            return node_1

            """    46 <piece_array_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<piece_array_init>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def sip_array_val(self):
        self.appendF(FIRST_SET["<sip_array_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    47 <sip_array_val>	=>	id	<id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_array_val>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.id_tail()

            return Identifier(token_0.value, token_0.line, token_0.col)

            """    48 <sip_array_val>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_array_val>_1"]:
            node_0 = self.ret_array()

            return node_0

            """    49 <sip_array_val>	=>	[	<array_element_sip_opt>	]    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_array_val>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.array_element_sip_opt()
            token_2 = self.tokens[self.pos]
            self.parse_token("]")

            # Create ArrayLiteral node
            node = ArrayLiteral(node_1, token_0.line, token_0.col)
            return node

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def sip_array_init(self):
        self.appendF(FIRST_SET["<sip_array_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    50 <sip_array_init>	=>	=	<sip_array_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_array_init>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("=")
            node_1 = self.sip_array_val()

            return node_1

            """    51 <sip_array_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_array_init>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def chars_array_val(self):
        self.appendF(FIRST_SET["<chars_array_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    52 <chars_array_val>	=>	id	<id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_array_val>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.id_tail()

            return Identifier(token_0.value, token_0.line, token_0.col)

            """    53 <chars_array_val>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_array_val>_1"]:
            node_0 = self.ret_array()

            return node_0

            """    54 <chars_array_val>	=>	[	<array_element_chars_opt>	]    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_array_val>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.array_element_chars_opt()
            token_2 = self.tokens[self.pos]
            self.parse_token("]")

            # Create ArrayLiteral node
            node = ArrayLiteral(node_1, token_0.line, token_0.col)
            return node

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def chars_array_init(self):
        self.appendF(FIRST_SET["<chars_array_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    55 <chars_array_init>	=>	=	<chars_array_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_array_init>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("=")
            node_1 = self.chars_array_val()

            return node_1

            """    56 <chars_array_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<chars_array_init>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_array_val(self):
        self.appendF(FIRST_SET["<flag_array_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    57 <flag_array_val>	=>	id	<id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_array_val>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.id_tail()

            return Identifier(token_0.value, token_0.line, token_0.col)

            """    58 <flag_array_val>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_array_val>_1"]:
            node_0 = self.ret_array()

            return node_0

            """    59 <flag_array_val>	=>	[	<array_element_flag_opt>	]    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_array_val>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.array_element_flag_opt()
            token_2 = self.tokens[self.pos]
            self.parse_token("]")

            # Create ArrayLiteral node
            node = ArrayLiteral(node_1, token_0.line, token_0.col)
            return node

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_array_init(self):
        self.appendF(FIRST_SET["<flag_array_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    60 <flag_array_init>	=>	=	<flag_array_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_array_init>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("=")
            node_1 = self.flag_array_val()

            return node_1

            """    61 <flag_array_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_array_init>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def table_array_val(self):
        self.appendF(FIRST_SET["<table_array_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    62 <table_array_val>	=>	id	<id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_array_val>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.id_tail()

            return Identifier(token_0.value, token_0.line, token_0.col)

            """    63 <table_array_val>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_array_val>_1"]:
            node_0 = self.ret_array()

            return node_0

            """    64 <table_array_val>	=>	[	<array_element_table_opt>	]    """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_array_val>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.array_element_table_opt()
            token_2 = self.tokens[self.pos]
            self.parse_token("]")

            # Create ArrayLiteral node
            node = ArrayLiteral(node_1, token_0.line, token_0.col)
            return node

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def table_array_init(self):
        self.appendF(FIRST_SET["<table_array_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    65 <table_array_init>	=>	=	<table_array_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_array_init>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("=")
            node_1 = self.table_array_val()

            return node_1

            """    66 <table_array_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_array_init>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def array_declare_tail_piece(self):
        self.appendF(FIRST_SET["<array_declare_tail_piece>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    67 <array_declare_tail_piece>	=>	,	id	<piece_array_init>	<array_declare_tail_piece>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_piece>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            token_1 = self.tokens[self.pos]
            self.parse_token("id")
            node_2 = self.piece_array_init()
            node_3 = self.array_declare_tail_piece()

            # Collect: [ArrayDecl("piece",CONTEXT,$1.value,$2)] + $3
            result = [ArrayDecl("piece",self._context_dimensions,token_1.value,node_2, token_1.line, token_1.col)] + node_3
            return result

            """    68 <array_declare_tail_piece>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_piece>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def array_declare_tail_sip(self):
        self.appendF(FIRST_SET["<array_declare_tail_sip>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    69 <array_declare_tail_sip>	=>	,	id	<sip_array_init>	<array_declare_tail_sip>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_sip>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            token_1 = self.tokens[self.pos]
            self.parse_token("id")
            node_2 = self.sip_array_init()
            node_3 = self.array_declare_tail_sip()

            # Collect: [ArrayDecl("sip",CONTEXT,$1.value,$2)] + $3
            result = [ArrayDecl("sip",self._context_dimensions,token_1.value,node_2, token_1.line, token_1.col)] + node_3
            return result

            """    70 <array_declare_tail_sip>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_sip>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def array_declare_tail_flag(self):
        self.appendF(FIRST_SET["<array_declare_tail_flag>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    71 <array_declare_tail_flag>	=>	,	id	<flag_array_init>	<array_declare_tail_flag>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_flag>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            token_1 = self.tokens[self.pos]
            self.parse_token("id")
            node_2 = self.flag_array_init()
            node_3 = self.array_declare_tail_flag()

            # Collect: [ArrayDecl("flag",CONTEXT,$1.value,$2)] + $3
            result = [ArrayDecl("flag",self._context_dimensions,token_1.value,node_2, token_1.line, token_1.col)] + node_3
            return result

            """    72 <array_declare_tail_flag>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_flag>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def array_declare_tail_chars(self):
        self.appendF(FIRST_SET["<array_declare_tail_chars>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    73 <array_declare_tail_chars>	=>	,	id	<chars_array_init>	<array_declare_tail_chars>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_chars>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            token_1 = self.tokens[self.pos]
            self.parse_token("id")
            node_2 = self.chars_array_init()
            node_3 = self.array_declare_tail_chars()

            # Collect: [ArrayDecl("chars",CONTEXT,$1.value,$2)] + $3
            result = [ArrayDecl("chars",self._context_dimensions,token_1.value,node_2, token_1.line, token_1.col)] + node_3
            return result

            """    74 <array_declare_tail_chars>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_chars>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def array_declare_tail_table(self):
        self.appendF(FIRST_SET["<array_declare_tail_table>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    75 <array_declare_tail_table>	=>	,	id	<table_array_init>	<array_declare_tail_table>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_table>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            token_1 = self.tokens[self.pos]
            self.parse_token("id")
            node_2 = self.table_array_init()
            node_3 = self.array_declare_tail_table()

            # Collect: [ArrayDecl(CONTEXT_TYPE,CONTEXT,$1.value,$2)] + $3
            result = [ArrayDecl(self._context_type,self._context_dimensions,token_1.value,node_2, token_1.line, token_1.col)] + node_3
            return result

            """    76 <array_declare_tail_table>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_declare_tail_table>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def dimensions(self):
        self.appendF(FIRST_SET["<dimensions>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    77 <dimensions>	=>	[	]	<dimensions_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<dimensions>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            token_1 = self.tokens[self.pos]
            self.parse_token("]")
            node_2 = self.dimensions_tail()

            # Count dimensions
            return 1 + ((node_2) if node_2 else 0)
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def dimensions_tail(self):
        self.appendF(FIRST_SET["<dimensions_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    78 <dimensions_tail>	=>	<dimensions>    """
        if self.tokens[self.pos].type in PREDICT_SET["<dimensions_tail>"]:
            node_0 = self.dimensions()

            return node_0

            """    79 <dimensions_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<dimensions_tail>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def flavor(self):
        self.appendF(FIRST_SET["<flavor>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    80 <flavor>	=>	<value>	<flavor_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flavor>"]:
            node_0 = self.value()
            node_1 = self.flavor_tail()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    81 <flavor>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flavor>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def value(self):
        self.appendF(FIRST_SET["<value>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    82 <value>	=>	<any_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<value>"]:
            node_0 = self.any_expr()

            return node_0

            """    83 <value>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_1"]:
            node_0 = self.ret_array()

            return node_0

            """    84 <value>	=>	[	<notation_val>	]    """
        elif self.tokens[self.pos].type in PREDICT_SET["<value>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.notation_val()
            token_2 = self.tokens[self.pos]
            self.parse_token("]")

            # If notation_val is None (empty), create empty ArrayLiteral
            if node_1 is None:
                return ArrayLiteral([], token_0.line, token_0.col)
            # If notation_val returns a list, create ArrayLiteral with those elements
            elif isinstance(node_1, list):
                return ArrayLiteral(node_1, token_0.line, token_0.col)
            # Otherwise return as-is
            else:
                return node_1

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def notation_val(self):
        self.appendF(FIRST_SET["<notation_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    85 <notation_val>	=>	<array_element>    """
        if self.tokens[self.pos].type in PREDICT_SET["<notation_val>"]:
            node_0 = self.array_element()

            return node_0

            """    86 <notation_val>	=>	id	<array_or_table>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<notation_val>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            # Set identifier context for subsequent parsing
            self._context_identifier = token_0.value
            self._context_identifier_line = token_0.line
            self._context_identifier_col = token_0.col
            node_1 = self.array_or_table()

            return node_1

            """    87 <notation_val>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<notation_val>_2"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def array_element(self):
        self.appendF(FIRST_SET["<array_element>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    88 <array_element>	=>	piece_lit	<element_value_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("piece_lit")
            node_1 = self.element_value_tail()

            # Collect: [Literal("piece", $0.value)] + $1
            result = [Literal("piece", token_0.value, token_0.line, token_0.col)] + node_1
            return result

            """    89 <array_element>	=>	sip_lit	<element_value_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("sip_lit")
            node_1 = self.element_value_tail()

            # Collect: [Literal("sip", $0.value)] + $1
            result = [Literal("sip", token_0.value, token_0.line, token_0.col)] + node_1
            return result

            """    90 <array_element>	=>	flag_lit	<element_value_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("flag_lit")
            node_1 = self.element_value_tail()

            # Collect: [Literal("flag", $0.value)] + $1
            result = [Literal("flag", token_0.value, token_0.line, token_0.col)] + node_1
            return result

            """    91 <array_element>	=>	chars_lit	<element_value_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("chars_lit")
            node_1 = self.element_value_tail()

            # Collect: [Literal("chars", $0.value)] + $1
            result = [Literal("chars", token_0.value, token_0.line, token_0.col)] + node_1
            return result

            """    92 <array_element>	=>	[	<notation_val>	]	<element_value_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.notation_val()
            token_2 = self.tokens[self.pos]
            self.parse_token("]")
            node_3 = self.element_value_tail()

            # Collect: [ArrayLiteral($1)] + $3
            result = [ArrayLiteral(node_1, token_0.line, token_0.col)] + node_3
            return result

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def element_value_tail(self):
        self.appendF(FIRST_SET["<element_value_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    93 <element_value_tail>	=>	,	<array_element_id>    """
        if self.tokens[self.pos].type in PREDICT_SET["<element_value_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            node_1 = self.array_element_id()

            # Collect: $1
            result = node_1
            return result

            """    94 <element_value_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<element_value_tail>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def array_element_id(self):
        self.appendF(FIRST_SET["<array_element_id>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    95 <array_element_id>	=>	id	<element_value_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_id>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.element_value_tail()

            # Collect: [Identifier($0.value)] + $1
            result = [Identifier(token_0.value, token_0.line, token_0.col)] + node_1
            return result

            """    96 <array_element_id>	=>	<array_element>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_id>_1"]:
            node_0 = self.array_element()

            return node_0

            """    97 <array_element_id>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_id>_2"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def array_element_piece(self):
        self.appendF(FIRST_SET["<array_element_piece>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    98 <array_element_piece>	=>	id	<element_piece_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_piece>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.element_piece_tail()

            # Collect: [Identifier($0.value)] + $1
            result = [Identifier(token_0.value, token_0.line, token_0.col)] + node_1
            return result

            """    99 <array_element_piece>	=>	piece_lit	<element_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_piece>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("piece_lit")
            node_1 = self.element_piece_tail()

            # Collect: [Literal("piece",$0.value)] + $1
            result = [Literal("piece",token_0.value, token_0.line, token_0.col)] + node_1
            return result

            """    100 <array_element_piece>	=>	[	<array_element_piece>	]	<element_piece_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_piece>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.array_element_piece()
            token_2 = self.tokens[self.pos]
            self.parse_token("]")
            node_3 = self.element_piece_tail()

            # Collect: [ArrayLiteral($1)] + $3
            result = [ArrayLiteral(node_1, token_0.line, token_0.col)] + node_3
            return result

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def array_element_piece_opt(self):
        self.appendF(FIRST_SET["<array_element_piece_opt>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    101 <array_element_piece_opt>	=>	<array_element_piece>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_piece_opt>"]:
            node_0 = self.array_element_piece()

            return node_0

            """    102 <array_element_piece_opt>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_piece_opt>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def element_piece_tail(self):
        self.appendF(FIRST_SET["<element_piece_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    103 <element_piece_tail>	=>	,	<array_element_piece>    """
        if self.tokens[self.pos].type in PREDICT_SET["<element_piece_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            node_1 = self.array_element_piece()

            # Collect: $1
            result = node_1
            return result

            """    104 <element_piece_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<element_piece_tail>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def array_element_sip(self):
        self.appendF(FIRST_SET["<array_element_sip>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    105 <array_element_sip>	=>	id	<element_sip_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_sip>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.element_sip_tail()

            # Collect: [Identifier($0.value)] + $1
            result = [Identifier(token_0.value, token_0.line, token_0.col)] + node_1
            return result

            """    106 <array_element_sip>	=>	sip_lit	<element_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_sip>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("sip_lit")
            node_1 = self.element_sip_tail()

            # Collect: [Literal("sip",$0.value)] + $1
            result = [Literal("sip",token_0.value, token_0.line, token_0.col)] + node_1
            return result

            """    107 <array_element_sip>	=>	[	<array_element_sip_opt>	]	<element_sip_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_sip>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.array_element_sip_opt()
            token_2 = self.tokens[self.pos]
            self.parse_token("]")
            node_3 = self.element_sip_tail()

            # Collect: [ArrayLiteral($1)] + $3
            result = [ArrayLiteral(node_1, token_0.line, token_0.col)] + node_3
            return result

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def array_element_sip_opt(self):
        self.appendF(FIRST_SET["<array_element_sip_opt>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    108 <array_element_sip_opt>	=>	<array_element_sip>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_sip_opt>"]:
            node_0 = self.array_element_sip()

            return node_0

            """    109 <array_element_sip_opt>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_sip_opt>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def element_sip_tail(self):
        self.appendF(FIRST_SET["<element_sip_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    110 <element_sip_tail>	=>	,	<array_element_sip>    """
        if self.tokens[self.pos].type in PREDICT_SET["<element_sip_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            node_1 = self.array_element_sip()

            # Collect: $1
            result = node_1
            return result

            """    111 <element_sip_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<element_sip_tail>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def array_element_chars(self):
        self.appendF(FIRST_SET["<array_element_chars>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    112 <array_element_chars>	=>	id	<element_chars_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_chars>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.element_chars_tail()

            # Collect: [Identifier($0.value)] + $1
            result = [Identifier(token_0.value, token_0.line, token_0.col)] + node_1
            return result

            """    113 <array_element_chars>	=>	chars_lit	<element_chars_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_chars>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("chars_lit")
            node_1 = self.element_chars_tail()

            # Collect: [Literal("chars",$0.value)] + $1
            result = [Literal("chars",token_0.value, token_0.line, token_0.col)] + node_1
            return result

            """    114 <array_element_chars>	=>	[	<array_element_chars_opt>	]	<element_chars_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_chars>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.array_element_chars_opt()
            token_2 = self.tokens[self.pos]
            self.parse_token("]")
            node_3 = self.element_chars_tail()

            # Collect: [ArrayLiteral($1)] + $3
            result = [ArrayLiteral(node_1, token_0.line, token_0.col)] + node_3
            return result

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def array_element_chars_opt(self):
        self.appendF(FIRST_SET["<array_element_chars_opt>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    115 <array_element_chars_opt>	=>	<array_element_chars>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_chars_opt>"]:
            node_0 = self.array_element_chars()

            return node_0

            """    116 <array_element_chars_opt>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_chars_opt>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def element_chars_tail(self):
        self.appendF(FIRST_SET["<element_chars_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    117 <element_chars_tail>	=>	,	<array_element_chars>    """
        if self.tokens[self.pos].type in PREDICT_SET["<element_chars_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            node_1 = self.array_element_chars()

            # Collect: $1
            result = node_1
            return result

            """    118 <element_chars_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<element_chars_tail>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def array_element_flag(self):
        self.appendF(FIRST_SET["<array_element_flag>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    119 <array_element_flag>	=>	id	<element_flag_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_flag>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.element_flag_tail()

            # Collect: [Identifier($0.value)] + $1
            result = [Identifier(token_0.value, token_0.line, token_0.col)] + node_1
            return result

            """    120 <array_element_flag>	=>	flag_lit	<element_flag_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_flag>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("flag_lit")
            node_1 = self.element_flag_tail()

            # Collect: [Literal("flag",$0.value)] + $1
            result = [Literal("flag",token_0.value, token_0.line, token_0.col)] + node_1
            return result

            """    121 <array_element_flag>	=>	[	<array_element_flag_opt>	]	<element_flag_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_flag>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.array_element_flag_opt()
            token_2 = self.tokens[self.pos]
            self.parse_token("]")
            node_3 = self.element_flag_tail()

            # Collect: [ArrayLiteral($1)] + $3
            result = [ArrayLiteral(node_1, token_0.line, token_0.col)] + node_3
            return result

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def array_element_flag_opt(self):
        self.appendF(FIRST_SET["<array_element_flag_opt>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    122 <array_element_flag_opt>	=>	<array_element_flag>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_flag_opt>"]:
            node_0 = self.array_element_flag()

            return node_0

            """    123 <array_element_flag_opt>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_flag_opt>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def element_flag_tail(self):
        self.appendF(FIRST_SET["<element_flag_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    124 <element_flag_tail>	=>	,	<array_element_id>    """
        if self.tokens[self.pos].type in PREDICT_SET["<element_flag_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            node_1 = self.array_element_id()

            # Collect: $1
            result = node_1
            return result

            """    125 <element_flag_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<element_flag_tail>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def array_element_table(self):
        self.appendF(FIRST_SET["<array_element_table>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    126 <array_element_table>	=>	<strict_table_expr>	<element_table_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_table>"]:
            node_0 = self.strict_table_expr()
            node_1 = self.element_table_tail()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def array_element_table_opt(self):
        self.appendF(FIRST_SET["<array_element_table_opt>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    127 <array_element_table_opt>	=>	<array_element_table>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_element_table_opt>"]:
            node_0 = self.array_element_table()

            return node_0

            """    128 <array_element_table_opt>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_element_table_opt>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def element_table_tail(self):
        self.appendF(FIRST_SET["<element_table_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    129 <element_table_tail>	=>	,	<array_element_table>    """
        if self.tokens[self.pos].type in PREDICT_SET["<element_table_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            node_1 = self.array_element_table()

            # Collect: $1
            result = node_1
            return result

            """    130 <element_table_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<element_table_tail>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def array_or_table(self):
        self.appendF(FIRST_SET["<array_or_table>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    131 <array_or_table>	=>	,	<array_element_id>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_or_table>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            node_1 = self.array_element_id()

            # Collect: [Identifier(CONTEXT_ID)] + $1
            result = [Identifier(self._context_identifier, self._context_identifier_line, self._context_identifier_col)] + node_1
            return result

            """    132 <array_or_table>	=>	=	<value>	;	<field_assignments>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_or_table>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("=")
            node_1 = self.value()
            token_2 = self.tokens[self.pos]
            self.parse_token(";")
            node_3 = self.field_assignments()

            # Collect: TableLiteral([(CONTEXT_ID,$1)] + $3)
            result = TableLiteral([(self._context_identifier,node_1, token_0.line, token_0.col)] + node_3)
            return result

            """    133 <array_or_table>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_or_table>_2"]:
            # Propagate expression
            return Identifier(self._context_identifier, self._context_identifier_line, self._context_identifier_col)


        log.info("Exit: " + self.tokens[self.pos].type)

    def field_assignments(self):
        self.appendF(FIRST_SET["<field_assignments>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    134 <field_assignments>	=>	id	=	<value>	;	<field_assignments>    """
        if self.tokens[self.pos].type in PREDICT_SET["<field_assignments>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            token_1 = self.tokens[self.pos]
            self.parse_token("=")
            node_2 = self.value()
            token_3 = self.tokens[self.pos]
            self.parse_token(";")
            node_4 = self.field_assignments()

            # Collect: [($0.value, $2, $1.line, $1.col)] + $4
            result = [(token_0.value, node_2, token_1.line, token_1.col)] + node_4
            return result

            """    135 <field_assignments>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<field_assignments>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def flavor_tail(self):
        self.appendF(FIRST_SET["<flavor_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    136 <flavor_tail>	=>	,	<value>	<flavor_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flavor_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            node_1 = self.value()
            node_2 = self.flavor_tail()

            # Collect: [$1] + $2
            result = [node_1] + node_2
            return result

            """    137 <flavor_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flavor_tail>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def accessor_tail(self):
        self.appendF(FIRST_SET["<accessor_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    138 <accessor_tail>	=>	<array_accessor>    """
        if self.tokens[self.pos].type in PREDICT_SET["<accessor_tail>"]:
            node_0 = self.array_accessor()

            return node_0

            """    139 <accessor_tail>	=>	<table_accessor>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<accessor_tail>_1"]:
            node_0 = self.table_accessor()

            return node_0

            """    140 <accessor_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<accessor_tail>_2"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def array_accessor(self):
        self.appendF(FIRST_SET["<array_accessor>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    141 <array_accessor>	=>	[	<array_accessor_val>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_accessor>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.array_accessor_val()

            # Build array accessor start
            return node_1
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def array_accessor_val(self):
        self.appendF(FIRST_SET["<array_accessor_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    142 <array_accessor_val>	=>	piece_lit	]	<accessor_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<array_accessor_val>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("piece_lit")
            token_1 = self.tokens[self.pos]
            self.parse_token("]")
            node_2 = self.accessor_tail()

            # Build array accessor chain
            def build_access(base):
                node = ArrayAccess(base, Literal("piece",token_0.value), token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_access

            """    143 <array_accessor_val>	=>	id	]	<accessor_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<array_accessor_val>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            token_1 = self.tokens[self.pos]
            self.parse_token("]")
            node_2 = self.accessor_tail()

            # Build array accessor chain
            def build_access(base):
                node = ArrayAccess(base, Identifier(token_0.value), token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_access

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def table_accessor(self):
        self.appendF(FIRST_SET["<table_accessor>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    144 <table_accessor>	=>	:	id	<accessor_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_accessor>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(":")
            token_1 = self.tokens[self.pos]
            self.parse_token("id")
            node_2 = self.accessor_tail()

            # Build table accessor chain
            def build_access(base):
                node = TableAccess(base, token_1.value, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_access
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def table_prototype(self):
        self.appendF(FIRST_SET["<table_prototype>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    145 <table_prototype>	=>	table	of	id	=	[	<required_decl>	]	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_prototype>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("table")
            token_1 = self.tokens[self.pos]
            self.parse_token("of")
            token_2 = self.tokens[self.pos]
            self.parse_token("id")
            token_3 = self.tokens[self.pos]
            self.parse_token("=")
            token_4 = self.tokens[self.pos]
            self.parse_token("[")
            node_5 = self.required_decl()
            token_6 = self.tokens[self.pos]
            self.parse_token("]")
            token_7 = self.tokens[self.pos]
            self.parse_token(";")

            # Create TablePrototype node
            node = TablePrototype(token_2.value, node_5, token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def required_decl(self):
        self.appendF(FIRST_SET["<required_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    146 <required_decl>	=>	<decl_head>	;	<required_decl_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<required_decl>"]:
            node_0 = self.decl_head()
            token_1 = self.tokens[self.pos]
            self.parse_token(";")
            node_2 = self.required_decl_tail()

            # Collect: [$0] + $2
            result = [node_0] + node_2
            return result
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def decl_head(self):
        self.appendF(FIRST_SET["<decl_head>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    147 <decl_head>	=>	<primitive_types_dims>	of	id    """
        if self.tokens[self.pos].type in PREDICT_SET["<decl_head>"]:
            node_0 = self.primitive_types_dims()
            token_1 = self.tokens[self.pos]
            self.parse_token("of")
            token_2 = self.tokens[self.pos]
            self.parse_token("id")

            # Create FieldDecl node
            node = FieldDecl(node_0.type, node_0.dims, token_2.value, token_1.line, token_1.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def primitive_types_dims(self):
        self.appendF(FIRST_SET["<primitive_types_dims>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    148 <primitive_types_dims>	=>	piece	<dimensions_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("piece")
            node_1 = self.dimensions_tail()

            # Create simple attribute object
            class PropagatedAttrs: pass
            result = PropagatedAttrs()
            result.type = "piece"
            result.dims = node_1
            return result

            """    149 <primitive_types_dims>	=>	sip	<dimensions_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("sip")
            node_1 = self.dimensions_tail()

            # Create simple attribute object
            class PropagatedAttrs: pass
            result = PropagatedAttrs()
            result.type = "sip"
            result.dims = node_1
            return result

            """    150 <primitive_types_dims>	=>	flag	<dimensions_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("flag")
            node_1 = self.dimensions_tail()

            # Create simple attribute object
            class PropagatedAttrs: pass
            result = PropagatedAttrs()
            result.type = "flag"
            result.dims = node_1
            return result

            """    151 <primitive_types_dims>	=>	chars	<dimensions_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("chars")
            node_1 = self.dimensions_tail()

            # Create simple attribute object
            class PropagatedAttrs: pass
            result = PropagatedAttrs()
            result.type = "chars"
            result.dims = node_1
            return result

            """    152 <primitive_types_dims>	=>	id	<dimensions_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<primitive_types_dims>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.dimensions_tail()

            # Create simple attribute object
            class PropagatedAttrs: pass
            result = PropagatedAttrs()
            result.type = token_0.value
            result.dims = node_1
            return result

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def required_decl_tail(self):
        self.appendF(FIRST_SET["<required_decl_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    153 <required_decl_tail>	=>	<required_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<required_decl_tail>"]:
            node_0 = self.required_decl()

            return node_0

            """    154 <required_decl_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<required_decl_tail>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def table_decl(self):
        self.appendF(FIRST_SET["<table_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    155 <table_decl>	=>	of	<table_declare>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_decl>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("of")
            node_1 = self.table_declare()
            token_2 = self.tokens[self.pos]
            self.parse_token(";")

            return node_1

            """    156 <table_decl>	=>	<table_array_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_decl>_1"]:
            node_0 = self.table_array_decl()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def table_declare(self):
        self.appendF(FIRST_SET["<table_declare>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    157 <table_declare>	=>	id	<table_init>	<table_declare_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_declare>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.table_init()
            node_2 = self.table_declare_tail()

            # Collect: [TableDecl(CONTEXT_TYPE,$0.value,$1)] + $2
            result = [TableDecl(self._context_type,token_0.value,node_1)] + node_2
            return result
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def table_init(self):
        self.appendF(FIRST_SET["<table_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    158 <table_init>	=>	=	<strict_table_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_init>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("=")
            node_1 = self.strict_table_expr()

            return node_1

            """    159 <table_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_init>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_table_expr(self):
        self.appendF(FIRST_SET["<strict_table_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    160 <strict_table_expr>	=>	[	<field_assignments>	]    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_table_expr>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.field_assignments()
            token_2 = self.tokens[self.pos]
            self.parse_token("]")

            # Create TableLiteral node
            node = TableLiteral(node_1, token_0.line, token_0.col)
            return node

            """    161 <strict_table_expr>	=>	<id>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_table_expr>_1"]:
            node_0 = self.id_()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def table_declare_tail(self):
        self.appendF(FIRST_SET["<table_declare_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    162 <table_declare_tail>	=>	,	<table_declare>    """
        if self.tokens[self.pos].type in PREDICT_SET["<table_declare_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            node_1 = self.table_declare()

            # Collect: $1
            result = node_1
            return result

            """    163 <table_declare_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<table_declare_tail>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def recipe_decl(self):
        self.appendF(FIRST_SET["<recipe_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    164 <recipe_decl>	=>	prepare	<serve_type>	(	<spice>	)	<platter>	<recipe_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<recipe_decl>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("prepare")
            node_1 = self.serve_type()
            token_2 = self.tokens[self.pos]
            self.parse_token("(")
            node_3 = self.spice()
            token_4 = self.tokens[self.pos]
            self.parse_token(")")
            node_5 = self.platter()
            node_6 = self.recipe_decl()

            # Collect: [RecipeDecl($1_data_type,$1_dimensions,$1_identifier,$3,$5)] + $6
            result = [RecipeDecl(node_1.data_type,node_1.dimensions,node_1.identifier,node_3,node_5, token_0.line, token_0.col)] + node_6
            return result

            """    165 <recipe_decl>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<recipe_decl>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def serve_type(self):
        self.appendF(FIRST_SET["<serve_type>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    166 <serve_type>	=>	<decl_head>    """
        if self.tokens[self.pos].type in PREDICT_SET["<serve_type>"]:
            node_0 = self.decl_head()

            return node_0
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def spice(self):
        self.appendF(FIRST_SET["<spice>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    167 <spice>	=>	<decl_head>	<spice_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<spice>"]:
            node_0 = self.decl_head()
            node_1 = self.spice_tail()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    168 <spice>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<spice>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def spice_tail(self):
        self.appendF(FIRST_SET["<spice_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    169 <spice_tail>	=>	,	<decl_head>	<spice_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<spice_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(",")
            node_1 = self.decl_head()
            node_2 = self.spice_tail()

            # Collect: [$1] + $2
            result = [node_1] + node_2
            return result

            """    170 <spice_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<spice_tail>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def platter(self):
        self.appendF(FIRST_SET["<platter>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    171 <platter>	=>	{	<local_decl>	<statements>	}    """
        if self.tokens[self.pos].type in PREDICT_SET["<platter>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("{")
            node_1 = self.local_decl()
            node_2 = self.statements()
            token_3 = self.tokens[self.pos]
            self.parse_token("}")

            # Manual code
            return (lambda decls, stmts: Platter([d for d in decls if isinstance(d, (IngrDecl, ArrayDecl, TableDecl))], [s for s in decls if isinstance(s, (Assignment, ExpressionStatement, CheckStatement, RepeatLoop, PassLoop, OrderRepeatLoop, MenuStatement, BreakStatement, ContinueStatement, ServeStatement))] + stmts))(node_1, node_2)
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def local_decl(self):
        self.appendF(FIRST_SET["<local_decl>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    172 <local_decl>	=>	piece	<piece_decl>	<local_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_decl>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("piece")
            node_1 = self.piece_decl()
            node_2 = self.local_decl()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    173 <local_decl>	=>	chars	<chars_decl>	<local_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("chars")
            node_1 = self.chars_decl()
            node_2 = self.local_decl()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    174 <local_decl>	=>	sip	<sip_decl>	<local_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("sip")
            node_1 = self.sip_decl()
            node_2 = self.local_decl()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    175 <local_decl>	=>	flag	<flag_decl>	<local_decl>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("flag")
            node_1 = self.flag_decl()
            node_2 = self.local_decl()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    176 <local_decl>	=>	id	<local_id_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            # Set context identifier BEFORE parsing so it's available for call_tail
            self._context_identifier = token_0.value
            self._context_identifier_line = token_0.line
            self._context_identifier_col = token_0.col
            node_1 = self.local_id_tail()

            # Collect: $1
            result = node_1
            return result

            """    177 <local_decl>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl>_5"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def local_id_tail(self):
        self.appendF(FIRST_SET["<local_id_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    178 <local_id_tail>	=>	of	<table_declare>	;	<local_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("of")
            node_1 = self.table_declare()
            token_2 = self.tokens[self.pos]
            self.parse_token(";")
            node_3 = self.local_decl()

            # Collect: [TableDecl(CONTEXT,$1)] + $3
            result = [TableDecl(self._context_dimensions,node_1)] + node_3
            return result

            """    179 <local_id_tail>	=>	[	<endsb_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.endsb_tail()

            # Collect: $1
            result = node_1
            return result

            """    180 <local_id_tail>	=>	<table_accessor>	<assignment_op>	<value>	;	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_2"]:
            node_0 = self.table_accessor()
            node_1 = self.assignment_op()
            node_2 = self.value()
            token_3 = self.tokens[self.pos]
            self.parse_token(";")
            node_4 = self.statements()

            # Collect: [Assignment(($0(Identifier(CONTEXT)) if $0 else Identifier(CONTEXT)), $1, $2)] + $4
            base_id = Identifier(self._context_identifier, self._context_identifier_line, self._context_identifier_col)
            result = [Assignment((node_0(base_id) if node_0 else base_id), node_1, node_2)] + node_4
            return result

            """    181 <local_id_tail>	=>	<assignment_op>	<value>	;	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_3"]:
            node_0 = self.assignment_op()
            node_1 = self.value()
            token_2 = self.tokens[self.pos]
            self.parse_token(";")
            node_3 = self.statements()

            # Collect: [Assignment(Identifier(CONTEXT), $0, $1)] + $3
            base_id = Identifier(self._context_identifier, self._context_identifier_line, self._context_identifier_col)
            result = [Assignment(base_id, node_0, node_1, token_2.line, token_2.col)] + node_3
            return result

            """    182 <local_id_tail>	=>	<tail1>	;	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail>_4"]:
            node_0 = self.tail1()
            token_1 = self.tokens[self.pos]
            self.parse_token(";")
            node_2 = self.statements()

            # Collect: [ExpressionStatement($0)] + $2
            result = [ExpressionStatement(node_0)] + node_2
            return result

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def endsb_tail(self):
        self.appendF(FIRST_SET["<endsb_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    183 <endsb_tail>	=>	]	<dimensions_tail>	of	id	<table_array_init>	;	<local_decl>    """
        if self.tokens[self.pos].type in PREDICT_SET["<endsb_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("]")
            node_1 = self.dimensions_tail()
            token_2 = self.tokens[self.pos]
            self.parse_token("of")
            token_3 = self.tokens[self.pos]
            self.parse_token("id")
            node_4 = self.table_array_init()
            token_5 = self.tokens[self.pos]
            self.parse_token(";")
            node_6 = self.local_decl()

            # Collect: [ArrayDecl(CONTEXT,$1,$3.value,$4)] + $6
            result = [ArrayDecl(self._context_dimensions,node_1,token_3.value,node_4, token_3.line, token_3.col)] + node_6
            return result

            """    184 <endsb_tail>	=>	<array_accessor_val>	<assignment_op>	<value>	;	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<endsb_tail>_1"]:
            node_0 = self.array_accessor_val()
            node_1 = self.assignment_op()
            node_2 = self.value()
            token_3 = self.tokens[self.pos]
            self.parse_token(";")
            node_4 = self.statements()

            # Collect: [Assignment(($0(CONTEXT) if $0 else CONTEXT), $1, $2)] + $4
            base = Identifier(self._context_identifier, self._context_identifier_line, self._context_identifier_col)
            result = [Assignment((node_0(base) if node_0 else base), node_1, node_2)] + node_4
            return result

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def assignment_op(self):
        self.appendF(FIRST_SET["<assignment_op>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    185 <assignment_op>	=>	=    """
        if self.tokens[self.pos].type in PREDICT_SET["<assignment_op>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("=")

            return self.tokens[self.pos - 1].value

            """    186 <assignment_op>	=>	+=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("+=")

            return self.tokens[self.pos - 1].value

            """    187 <assignment_op>	=>	-=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("-=")

            return self.tokens[self.pos - 1].value

            """    188 <assignment_op>	=>	*=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("*=")

            return self.tokens[self.pos - 1].value

            """    189 <assignment_op>	=>	/=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("/=")

            return self.tokens[self.pos - 1].value

            """    190 <assignment_op>	=>	%=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<assignment_op>_5"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("%=")

            return self.tokens[self.pos - 1].value

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def statements(self):
        self.appendF(FIRST_SET["<statements>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    191 <statements>	=>	<id_statements>	<statements>    """
        if self.tokens[self.pos].type in PREDICT_SET["<statements>"]:
            node_0 = self.id_statements()
            node_1 = self.statements()

            # Collect: $0 + $1
            result = node_0 + node_1
            return result

            """    192 <statements>	=>	<built_in_rec_call>	;	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_1"]:
            node_0 = self.built_in_rec_call()
            token_1 = self.tokens[self.pos]
            self.parse_token(";")
            node_2 = self.statements()

            # Collect: [ExpressionStatement($0)] + $2
            result = [ExpressionStatement(node_0)] + node_2
            return result

            """    193 <statements>	=>	<conditional_st>	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_2"]:
            node_0 = self.conditional_st()
            node_1 = self.statements()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    194 <statements>	=>	<looping_st>	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_3"]:
            node_0 = self.looping_st()
            node_1 = self.statements()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    195 <statements>	=>	<jump_serve>	<statements>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_4"]:
            node_0 = self.jump_serve()
            node_1 = self.statements()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    196 <statements>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements>_5"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def id_statements(self):
        self.appendF(FIRST_SET["<id_statements>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    197 <id_statements>	=>	id	<id_statements_ext>	<statements>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            # Set context identifier BEFORE parsing so it's available for call_tail
            self._context_identifier = token_0.value
            self._context_identifier_line = token_0.line
            self._context_identifier_col = token_0.col
            node_1 = self.id_statements_ext()
            node_2 = self.statements()

            # Manual code
            return [node_1] + node_2
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def id_statements_ext(self):
        self.appendF(FIRST_SET["<id_statements_ext>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    198 <id_statements_ext>	=>	<tail1>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements_ext>"]:
            node_0 = self.tail1()
            token_1 = self.tokens[self.pos]
            self.parse_token(";")

            # Create ExpressionStatement node
            node = ExpressionStatement(node_0, token_1.line, token_1.col)
            return node

            """    199 <id_statements_ext>	=>	<assignment_st>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<id_statements_ext>_1"]:
            node_0 = self.assignment_st()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def tail1(self):
        self.appendF(FIRST_SET["<tail1>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    200 <tail1>	=>	<call_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<tail1>"]:
            node_0 = self.call_tail()

            return node_0
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def call_tail(self):
        self.appendF(FIRST_SET["<call_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    201 <call_tail>	=>	(	<flavor>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<call_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("(")
            node_1 = self.flavor()
            token_2 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall(self._context_identifier, node_1, token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def assignment_st(self):
        self.appendF(FIRST_SET["<assignment_st>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    202 <assignment_st>	=>	<accessor_tail>	<assignment_op>	<value>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<assignment_st>"]:
            node_0 = self.accessor_tail()
            node_1 = self.assignment_op()
            node_2 = self.value()
            token_3 = self.tokens[self.pos]
            self.parse_token(";")

            # Create Assignment node
            target = Identifier(self._context_identifier, self._context_identifier_line, self._context_identifier_col)
            accessor = node_0
            if accessor:
                target = accessor(target)
            node = Assignment(target, node_1, node_2, token_3.line, token_3.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def built_in_rec_call(self):
        self.appendF(FIRST_SET["<built_in_rec_call>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    203 <built_in_rec_call>	=>	<built_in_rec>    """
        if self.tokens[self.pos].type in PREDICT_SET["<built_in_rec_call>"]:
            node_0 = self.built_in_rec()

            return node_0
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def built_in_rec(self):
        self.appendF(FIRST_SET["<built_in_rec>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    204 <built_in_rec>	=>	append	(	<strict_array_expr>	,	<value>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("append")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_array_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(",")
            node_4 = self.value()
            token_5 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("append", [node_2, node_4], token_0.line, token_0.col)
            return node

            """    205 <built_in_rec>	=>	bill	(	<strict_chars_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("bill")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_chars_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("bill", [node_2], token_0.line, token_0.col)
            return node

            """    206 <built_in_rec>	=>	copy	(	<strict_chars_expr>	,	<strict_piece_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("copy")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_chars_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(",")
            node_4 = self.strict_piece_expr()
            token_5 = self.tokens[self.pos]
            self.parse_token(",")
            node_6 = self.strict_piece_expr()
            token_7 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("copy", [node_2, node_4, node_6], token_0.line, token_0.col)
            return node

            """    207 <built_in_rec>	=>	cut	(	<strict_sip_expr>	,	<strict_sip_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("cut")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_sip_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(",")
            node_4 = self.strict_sip_expr()
            token_5 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("cut", [node_2, node_4], token_0.line, token_0.col)
            return node

            """    208 <built_in_rec>	=>	fact	(	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("fact")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_piece_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("fact", [node_2], token_0.line, token_0.col)
            return node

            """    209 <built_in_rec>	=>	matches	(	<strict_datas_expr>	,	<strict_datas_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_5"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("matches")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_datas_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(",")
            node_4 = self.strict_datas_expr()
            token_5 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("matches", [node_2, node_4], token_0.line, token_0.col)
            return node

            """    210 <built_in_rec>	=>	pow	(	<strict_piece_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_6"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("pow")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_piece_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(",")
            node_4 = self.strict_piece_expr()
            token_5 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("pow", [node_2, node_4], token_0.line, token_0.col)
            return node

            """    211 <built_in_rec>	=>	rand	(	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_7"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("rand")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            token_2 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("rand", [], token_0.line, token_0.col)
            return node

            """    212 <built_in_rec>	=>	remove	(	<strict_array_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_8"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("remove")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_array_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(",")
            node_4 = self.strict_piece_expr()
            token_5 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("remove", [node_2, node_4], token_0.line, token_0.col)
            return node

            """    213 <built_in_rec>	=>	reverse	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_9"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("reverse")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_array_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("reverse", [node_2], token_0.line, token_0.col)
            return node

            """    214 <built_in_rec>	=>	search	(	<strict_array_expr>	,	<value>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_10"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("search")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_array_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(",")
            node_4 = self.value()
            token_5 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("search", [node_2, node_4], token_0.line, token_0.col)
            return node

            """    215 <built_in_rec>	=>	size	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_11"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("size")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_array_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("size", [node_2], token_0.line, token_0.col)
            return node

            """    216 <built_in_rec>	=>	sort	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_12"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("sort")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_array_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("sort", [node_2], token_0.line, token_0.col)
            return node

            """    217 <built_in_rec>	=>	sqrt	(	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_13"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("sqrt")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_piece_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("sqrt", [node_2], token_0.line, token_0.col)
            return node

            """    218 <built_in_rec>	=>	take	(	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_14"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("take")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            token_2 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("take", [], token_0.line, token_0.col)
            return node

            """    219 <built_in_rec>	=>	tochars	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_15"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("tochars")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.any_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("tochars", [node_2], token_0.line, token_0.col)
            return node

            """    220 <built_in_rec>	=>	topiece	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_16"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("topiece")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.any_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("topiece", [node_2], token_0.line, token_0.col)
            return node

            """    221 <built_in_rec>	=>	tosip	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<built_in_rec>_17"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("tosip")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.any_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("tosip", [node_2], token_0.line, token_0.col)
            return node

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def conditional_st(self):
        self.appendF(FIRST_SET["<conditional_st>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    222 <conditional_st>	=>	<cond_check>    """
        if self.tokens[self.pos].type in PREDICT_SET["<conditional_st>"]:
            node_0 = self.cond_check()

            return node_0

            """    223 <conditional_st>	=>	<cond_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<conditional_st>_1"]:
            node_0 = self.cond_menu()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def cond_check(self):
        self.appendF(FIRST_SET["<cond_check>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    224 <cond_check>	=>	check	(	<strict_flag_expr>	)	<platter>	<alt_clause>	<instead_clause>    """
        if self.tokens[self.pos].type in PREDICT_SET["<cond_check>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("check")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_flag_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")
            node_4 = self.platter()
            node_5 = self.alt_clause()
            node_6 = self.instead_clause()

            # Create CheckStatement node
            node = CheckStatement(node_2, node_4, node_5, node_6, token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def alt_clause(self):
        self.appendF(FIRST_SET["<alt_clause>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    225 <alt_clause>	=>	alt	(	<strict_flag_expr>	)	<platter>	<alt_clause>    """
        if self.tokens[self.pos].type in PREDICT_SET["<alt_clause>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("alt")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_flag_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")
            node_4 = self.platter()
            node_5 = self.alt_clause()

            # Collect: [($2,$4)] + $5
            result = [(node_2,node_4)] + node_5
            return result

            """    226 <alt_clause>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<alt_clause>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def instead_clause(self):
        self.appendF(FIRST_SET["<instead_clause>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    227 <instead_clause>	=>	instead	<platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<instead_clause>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("instead")
            node_1 = self.platter()

            return node_1

            """    228 <instead_clause>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<instead_clause>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def cond_menu(self):
        self.appendF(FIRST_SET["<cond_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    229 <cond_menu>	=>	menu	(	<strict_piece_chars_expr>	)	<menu_platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<cond_menu>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("menu")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_piece_chars_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")
            node_4 = self.menu_platter()

            # Create MenuStatement node
            node = MenuStatement(node_2, node_4, token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def menu_platter(self):
        self.appendF(FIRST_SET["<menu_platter>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    230 <menu_platter>	=>	{	<choice_clause>	<usual_clause>	}    """
        if self.tokens[self.pos].type in PREDICT_SET["<menu_platter>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("{")
            node_1 = self.choice_clause()
            node_2 = self.usual_clause()
            token_3 = self.tokens[self.pos]
            self.parse_token("}")

            # Collect: $1 + $2
            result = node_1 + node_2
            return result
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def choice_clause(self):
        self.appendF(FIRST_SET["<choice_clause>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    231 <choice_clause>	=>	choice	<choice_val>	:	<statements_menu>	<choice_clause>    """
        if self.tokens[self.pos].type in PREDICT_SET["<choice_clause>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("choice")
            node_1 = self.choice_val()
            token_2 = self.tokens[self.pos]
            self.parse_token(":")
            node_3 = self.statements_menu()
            node_4 = self.choice_clause()

            # Collect: [CaseClause($1,$3)] + $4
            result = [CaseClause(node_1,node_3)] + node_4
            return result

            """    232 <choice_clause>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_clause>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def choice_val(self):
        self.appendF(FIRST_SET["<choice_val>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    233 <choice_val>	=>	piece_lit    """
        if self.tokens[self.pos].type in PREDICT_SET["<choice_val>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("piece_lit")

            # Create Literal node
            node = Literal("piece", token_0.value, token_0.line, token_0.col)
            return node

            """    234 <choice_val>	=>	chars_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_val>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("chars_lit")

            # Create Literal node
            node = Literal("chars", token_0.value, token_0.line, token_0.col)
            return node

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def statements_menu(self):
        self.appendF(FIRST_SET["<statements_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    235 <statements_menu>	=>	<id_statements_menu>	<statements_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<statements_menu>"]:
            node_0 = self.id_statements_menu()
            node_1 = self.statements_menu()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    236 <statements_menu>	=>	<built_in_rec_call>	;	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_1"]:
            node_0 = self.built_in_rec_call()
            token_1 = self.tokens[self.pos]
            self.parse_token(";")
            node_2 = self.statements_menu()

            # Collect: [ExpressionStatement($0)] + $2
            result = [ExpressionStatement(node_0)] + node_2
            return result

            """    237 <statements_menu>	=>	<conditional_st_menu>	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_2"]:
            node_0 = self.conditional_st_menu()
            node_1 = self.statements_menu()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    238 <statements_menu>	=>	<looping_st>	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_3"]:
            node_0 = self.looping_st()
            node_1 = self.statements_menu()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    239 <statements_menu>	=>	<jump_stop>	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_4"]:
            node_0 = self.jump_stop()
            node_1 = self.statements_menu()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    240 <statements_menu>	=>	<jump_serve>	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_5"]:
            node_0 = self.jump_serve()
            node_1 = self.statements_menu()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    241 <statements_menu>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_menu>_6"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def id_statements_menu(self):
        self.appendF(FIRST_SET["<id_statements_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    242 <id_statements_menu>	=>	id	<id_statements_ext>	<statements_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements_menu>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.id_statements_ext()
            node_2 = self.statements_menu()

            return node_1
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def conditional_st_menu(self):
        self.appendF(FIRST_SET["<conditional_st_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    243 <conditional_st_menu>	=>	<cond_check_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<conditional_st_menu>"]:
            node_0 = self.cond_check_menu()

            return node_0

            """    244 <conditional_st_menu>	=>	<cond_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<conditional_st_menu>_1"]:
            node_0 = self.cond_menu()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def cond_check_menu(self):
        self.appendF(FIRST_SET["<cond_check_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    245 <cond_check_menu>	=>	check	(	<strict_flag_expr>	)	<menu_check_platter>	<alt_clause>	<instead_clause>    """
        if self.tokens[self.pos].type in PREDICT_SET["<cond_check_menu>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("check")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_flag_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")
            node_4 = self.menu_check_platter()
            node_5 = self.alt_clause()
            node_6 = self.instead_clause()

            # Create CheckStatement node
            node = CheckStatement(node_2, node_4, node_5, node_6, token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def menu_check_platter(self):
        self.appendF(FIRST_SET["<menu_check_platter>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    246 <menu_check_platter>	=>	{	<local_decl_menu>	<statements_menu>	}    """
        if self.tokens[self.pos].type in PREDICT_SET["<menu_check_platter>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("{")
            node_1 = self.local_decl_menu()
            node_2 = self.statements_menu()
            token_3 = self.tokens[self.pos]
            self.parse_token("}")

            # Create Platter node
            node = Platter(node_1, node_2, token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def local_decl_menu(self):
        self.appendF(FIRST_SET["<local_decl_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    247 <local_decl_menu>	=>	piece	<piece_decl>	<local_decl_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("piece")
            node_1 = self.piece_decl()
            node_2 = self.local_decl_menu()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    248 <local_decl_menu>	=>	chars	<chars_decl>	<local_decl_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("chars")
            node_1 = self.chars_decl()
            node_2 = self.local_decl_menu()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    249 <local_decl_menu>	=>	sip	<sip_decl>	<local_decl_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("sip")
            node_1 = self.sip_decl()
            node_2 = self.local_decl_menu()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    250 <local_decl_menu>	=>	flag	<flag_decl>	<local_decl_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("flag")
            node_1 = self.flag_decl()
            node_2 = self.local_decl_menu()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    251 <local_decl_menu>	=>	id	<local_id_tail_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.local_id_tail_menu()

            # Collect: $1
            result = node_1
            return result

            """    252 <local_decl_menu>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_menu>_5"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def local_id_tail_menu(self):
        self.appendF(FIRST_SET["<local_id_tail_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    253 <local_id_tail_menu>	=>	of	<table_declare>	;	<local_decl_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("of")
            node_1 = self.table_declare()
            token_2 = self.tokens[self.pos]
            self.parse_token(";")
            node_3 = self.local_decl_menu()

            # Collect: [TableDecl(CONTEXT,$1)] + $3
            result = [TableDecl(self._context_dimensions,node_1)] + node_3
            return result

            """    254 <local_id_tail_menu>	=>	[	<endsb_tail_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.endsb_tail_menu()

            # Collect: $1
            result = node_1
            return result

            """    255 <local_id_tail_menu>	=>	<table_accessor>	<assignment_op>	<value>	;	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_2"]:
            node_0 = self.table_accessor()
            node_1 = self.assignment_op()
            node_2 = self.value()
            token_3 = self.tokens[self.pos]
            self.parse_token(";")
            node_4 = self.statements_menu()

            # Collect: [Assignment(($0(CONTEXT) if $0 else CONTEXT), $1, $2)] + $4
            result = [Assignment((node_0(self._context_dimensions, token_3.line, token_3.col) if node_0 else self._context_dimensions), node_1, node_2)] + node_4
            return result

            """    256 <local_id_tail_menu>	=>	<assignment_op>	<value>	;	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_3"]:
            node_0 = self.assignment_op()
            node_1 = self.value()
            token_2 = self.tokens[self.pos]
            self.parse_token(";")
            node_3 = self.statements_menu()

            # Collect: [Assignment(CONTEXT, $0, $1)] + $3
            result = [Assignment(self._context_dimensions, node_0, node_1, token_2.line, token_2.col)] + node_3
            return result

            """    257 <local_id_tail_menu>	=>	<tail1>	;	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_menu>_4"]:
            node_0 = self.tail1()
            token_1 = self.tokens[self.pos]
            self.parse_token(";")
            node_2 = self.statements_menu()

            # Collect: [ExpressionStatement($0)] + $2
            result = [ExpressionStatement(node_0)] + node_2
            return result

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def endsb_tail_menu(self):
        self.appendF(FIRST_SET["<endsb_tail_menu>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    258 <endsb_tail_menu>	=>	]	<dimensions_tail>	of	id	<table_array_init>	;	<local_decl_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<endsb_tail_menu>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("]")
            node_1 = self.dimensions_tail()
            token_2 = self.tokens[self.pos]
            self.parse_token("of")
            token_3 = self.tokens[self.pos]
            self.parse_token("id")
            node_4 = self.table_array_init()
            token_5 = self.tokens[self.pos]
            self.parse_token(";")
            node_6 = self.local_decl_menu()

            # Collect: [ArrayDecl(CONTEXT,$1,$3.value,$4)] + $6
            result = [ArrayDecl(self._context_dimensions,node_1,token_3.value,node_4, token_3.line, token_3.col)] + node_6
            return result

            """    259 <endsb_tail_menu>	=>	<array_accessor_val>	<assignment_op>	<value>	;	<statements_menu>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<endsb_tail_menu>_1"]:
            node_0 = self.array_accessor_val()
            node_1 = self.assignment_op()
            node_2 = self.value()
            token_3 = self.tokens[self.pos]
            self.parse_token(";")
            node_4 = self.statements_menu()

            # Collect: [Assignment(($0(CONTEXT) if $0 else CONTEXT), $1, $2)] + $4
            base = Identifier(self._context_identifier, self._context_identifier_line, self._context_identifier_col)
            result = [Assignment((node_0(base) if node_0 else base), node_1, node_2)] + node_4
            return result

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def looping_st(self):
        self.appendF(FIRST_SET["<looping_st>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    260 <looping_st>	=>	<loop_pass>    """
        if self.tokens[self.pos].type in PREDICT_SET["<looping_st>"]:
            node_0 = self.loop_pass()

            return node_0

            """    261 <looping_st>	=>	<loop_repeat>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<looping_st>_1"]:
            node_0 = self.loop_repeat()

            return node_0

            """    262 <looping_st>	=>	<loop_order>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<looping_st>_2"]:
            node_0 = self.loop_order()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def loop_pass(self):
        self.appendF(FIRST_SET["<loop_pass>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    263 <loop_pass>	=>	pass	(	<initialization>	<update>	<strict_flag_expr>	)	<loop_platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_pass>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("pass")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.initialization()
            node_3 = self.update()
            node_4 = self.strict_flag_expr()
            token_5 = self.tokens[self.pos]
            self.parse_token(")")
            node_6 = self.loop_platter()

            # Create PassLoop node
            node = PassLoop(node_2, node_3, node_4, node_6, token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def initialization(self):
        self.appendF(FIRST_SET["<initialization>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    264 <initialization>	=>	id	<loop_init>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<initialization>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.loop_init()
            token_2 = self.tokens[self.pos]
            self.parse_token(";")

            # Create Assignment node
            node = Assignment(Identifier(token_0.value, token_0.line, token_0.col), "=", node_1, token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def loop_init(self):
        self.appendF(FIRST_SET["<loop_init>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    265 <loop_init>	=>	=	<strict_piece_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_init>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("=")
            node_1 = self.strict_piece_expr()

            return node_1

            """    266 <loop_init>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<loop_init>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def update(self):
        self.appendF(FIRST_SET["<update>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    267 <update>	=>	id	<accessor_tail>	<assignment_op>	<strict_piece_expr>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<update>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.accessor_tail()
            node_2 = self.assignment_op()
            node_3 = self.strict_piece_expr()
            token_4 = self.tokens[self.pos]
            self.parse_token(";")

            # Create Assignment node
            target = Identifier(token_0.value, token_0.line, token_0.col)
            accessor = node_1
            if accessor:
                target = accessor(target)
            node = Assignment(target, node_2, node_3, token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def loop_platter(self):
        self.appendF(FIRST_SET["<loop_platter>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    268 <loop_platter>	=>	{	<local_decl_loop>	<statements_loop>	}    """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_platter>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("{")
            node_1 = self.local_decl_loop()
            node_2 = self.statements_loop()
            token_3 = self.tokens[self.pos]
            self.parse_token("}")

            # Create Platter node
            node = Platter(node_1, node_2, token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def local_decl_loop(self):
        self.appendF(FIRST_SET["<local_decl_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    269 <local_decl_loop>	=>	piece	<piece_decl>	<local_decl_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("piece")
            node_1 = self.piece_decl()
            node_2 = self.local_decl_loop()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    270 <local_decl_loop>	=>	chars	<chars_decl>	<local_decl_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("chars")
            node_1 = self.chars_decl()
            node_2 = self.local_decl_loop()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    271 <local_decl_loop>	=>	sip	<sip_decl>	<local_decl_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("sip")
            node_1 = self.sip_decl()
            node_2 = self.local_decl_loop()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    272 <local_decl_loop>	=>	flag	<flag_decl>	<local_decl_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("flag")
            node_1 = self.flag_decl()
            node_2 = self.local_decl_loop()

            # Collect: $1 + $2
            result = node_1 + node_2
            return result

            """    273 <local_decl_loop>	=>	id	<local_id_tail_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.local_id_tail_loop()

            # Collect: $1
            result = node_1
            return result

            """    274 <local_decl_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_decl_loop>_5"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def local_id_tail_loop(self):
        self.appendF(FIRST_SET["<local_id_tail_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    275 <local_id_tail_loop>	=>	of	<table_declare>	;	<local_decl_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("of")
            node_1 = self.table_declare()
            token_2 = self.tokens[self.pos]
            self.parse_token(";")
            node_3 = self.local_decl_loop()

            # Collect: [TableDecl(CONTEXT,$1)] + $3
            result = [TableDecl(self._context_dimensions,node_1)] + node_3
            return result

            """    276 <local_id_tail_loop>	=>	[	<endsb_tail_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.endsb_tail_loop()

            # Collect: $1
            result = node_1
            return result

            """    277 <local_id_tail_loop>	=>	<table_accessor>	<assignment_op>	<value>	;	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_2"]:
            node_0 = self.table_accessor()
            node_1 = self.assignment_op()
            node_2 = self.value()
            token_3 = self.tokens[self.pos]
            self.parse_token(";")
            node_4 = self.statements_loop()

            # Collect: [Assignment(($0(CONTEXT) if $0 else CONTEXT), $1, $2)] + $4
            result = [Assignment((node_0(self._context_dimensions, token_3.line, token_3.col) if node_0 else self._context_dimensions), node_1, node_2)] + node_4
            return result

            """    278 <local_id_tail_loop>	=>	<assignment_op>	<value>	;	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_3"]:
            node_0 = self.assignment_op()
            node_1 = self.value()
            token_2 = self.tokens[self.pos]
            self.parse_token(";")
            node_3 = self.statements_loop()

            # Collect: [Assignment(CONTEXT, $0, $1)] + $3
            result = [Assignment(self._context_dimensions, node_0, node_1, token_2.line, token_2.col)] + node_3
            return result

            """    279 <local_id_tail_loop>	=>	<tail1>	;	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<local_id_tail_loop>_4"]:
            node_0 = self.tail1()
            token_1 = self.tokens[self.pos]
            self.parse_token(";")
            node_2 = self.statements_loop()

            # Collect: [ExpressionStatement($0)] + $2
            result = [ExpressionStatement(node_0)] + node_2
            return result

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def endsb_tail_loop(self):
        self.appendF(FIRST_SET["<endsb_tail_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    280 <endsb_tail_loop>	=>	]	<dimensions_tail>	of	id	<table_array_init>	;	<local_decl_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<endsb_tail_loop>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("]")
            node_1 = self.dimensions_tail()
            token_2 = self.tokens[self.pos]
            self.parse_token("of")
            token_3 = self.tokens[self.pos]
            self.parse_token("id")
            node_4 = self.table_array_init()
            token_5 = self.tokens[self.pos]
            self.parse_token(";")
            node_6 = self.local_decl_loop()

            # Collect: [ArrayDecl(CONTEXT,$1,$3.value,$4)] + $6
            result = [ArrayDecl(self._context_dimensions,node_1,token_3.value,node_4, token_3.line, token_3.col)] + node_6
            return result

            """    281 <endsb_tail_loop>	=>	<array_accessor_val>	<assignment_op>	<value>	;	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<endsb_tail_loop>_1"]:
            node_0 = self.array_accessor_val()
            node_1 = self.assignment_op()
            node_2 = self.value()
            token_3 = self.tokens[self.pos]
            self.parse_token(";")
            node_4 = self.statements_loop()

            # Collect: [Assignment(($0(CONTEXT) if $0 else CONTEXT), $1, $2)] + $4
            base = Identifier(self._context_identifier, self._context_identifier_line, self._context_identifier_col)
            result = [Assignment((node_0(base) if node_0 else base), node_1, node_2)] + node_4
            return result

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def statements_loop(self):
        self.appendF(FIRST_SET["<statements_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    282 <statements_loop>	=>	<id_statements_loop>	<statements_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<statements_loop>"]:
            node_0 = self.id_statements_loop()
            node_1 = self.statements_loop()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    283 <statements_loop>	=>	<built_in_rec_call>	;	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_1"]:
            node_0 = self.built_in_rec_call()
            token_1 = self.tokens[self.pos]
            self.parse_token(";")
            node_2 = self.statements_loop()

            # Collect: [ExpressionStatement($0)] + $2
            result = [ExpressionStatement(node_0)] + node_2
            return result

            """    284 <statements_loop>	=>	<conditional_st_loop>	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_2"]:
            node_0 = self.conditional_st_loop()
            node_1 = self.statements_loop()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    285 <statements_loop>	=>	<looping_st>	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_3"]:
            node_0 = self.looping_st()
            node_1 = self.statements_loop()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    286 <statements_loop>	=>	<jump_st>	<statements_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_4"]:
            node_0 = self.jump_st()
            node_1 = self.statements_loop()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    287 <statements_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<statements_loop>_5"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def id_statements_loop(self):
        self.appendF(FIRST_SET["<id_statements_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    288 <id_statements_loop>	=>	id	<id_statements_ext>	<statements_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements_loop>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.id_statements_ext()
            node_2 = self.statements_loop()

            return node_1
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def conditional_st_loop(self):
        self.appendF(FIRST_SET["<conditional_st_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    289 <conditional_st_loop>	=>	<cond_check_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<conditional_st_loop>"]:
            node_0 = self.cond_check_loop()

            return node_0

            """    290 <conditional_st_loop>	=>	<cond_menu_loop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<conditional_st_loop>_1"]:
            node_0 = self.cond_menu_loop()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def cond_check_loop(self):
        self.appendF(FIRST_SET["<cond_check_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    291 <cond_check_loop>	=>	check	(	<strict_flag_expr>	)	<loop_platter>	<alt_clause_loop>	<instead_clause_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<cond_check_loop>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("check")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_flag_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")
            node_4 = self.loop_platter()
            node_5 = self.alt_clause_loop()
            node_6 = self.instead_clause_loop()

            # Create CheckStatement node
            node = CheckStatement(node_2, node_4, node_5, node_6, token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def alt_clause_loop(self):
        self.appendF(FIRST_SET["<alt_clause_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    292 <alt_clause_loop>	=>	alt	(	<strict_flag_expr>	)	<loop_platter>	<alt_clause_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<alt_clause_loop>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("alt")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_flag_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")
            node_4 = self.loop_platter()
            node_5 = self.alt_clause_loop()

            # Collect: [($2,$4)] + $5
            result = [(node_2,node_4)] + node_5
            return result

            """    293 <alt_clause_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<alt_clause_loop>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def instead_clause_loop(self):
        self.appendF(FIRST_SET["<instead_clause_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    294 <instead_clause_loop>	=>	instead	<loop_platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<instead_clause_loop>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("instead")
            node_1 = self.loop_platter()

            return node_1

            """    295 <instead_clause_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<instead_clause_loop>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def cond_menu_loop(self):
        self.appendF(FIRST_SET["<cond_menu_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    296 <cond_menu_loop>	=>	menu	(	<strict_piece_chars_expr>	)	<menu_loop_platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<cond_menu_loop>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("menu")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_piece_chars_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")
            node_4 = self.menu_loop_platter()

            # Create MenuStatement node
            node = MenuStatement(node_2, node_4, token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def menu_loop_platter(self):
        self.appendF(FIRST_SET["<menu_loop_platter>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    297 <menu_loop_platter>	=>	{	<choice_clause_loop>	<usual_clause_loop>	}    """
        if self.tokens[self.pos].type in PREDICT_SET["<menu_loop_platter>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("{")
            node_1 = self.choice_clause_loop()
            node_2 = self.usual_clause_loop()
            token_3 = self.tokens[self.pos]
            self.parse_token("}")

            # Collect: $1 + $2
            result = node_1 + node_2
            return result
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def choice_clause_loop(self):
        self.appendF(FIRST_SET["<choice_clause_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    298 <choice_clause_loop>	=>	choice	<choice_val>	:	<choice_usual_loop_st>	<choice_clause_loop>    """
        if self.tokens[self.pos].type in PREDICT_SET["<choice_clause_loop>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("choice")
            node_1 = self.choice_val()
            token_2 = self.tokens[self.pos]
            self.parse_token(":")
            node_3 = self.choice_usual_loop_st()
            node_4 = self.choice_clause_loop()

            # Collect: [CaseClause($1,$3)] + $4
            result = [CaseClause(node_1,node_3)] + node_4
            return result

            """    299 <choice_clause_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_clause_loop>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def usual_clause_loop(self):
        self.appendF(FIRST_SET["<usual_clause_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    300 <usual_clause_loop>	=>	usual	:	<choice_usual_loop_st>    """
        if self.tokens[self.pos].type in PREDICT_SET["<usual_clause_loop>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("usual")
            token_1 = self.tokens[self.pos]
            self.parse_token(":")
            node_2 = self.choice_usual_loop_st()

            return node_2

            """    301 <usual_clause_loop>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<usual_clause_loop>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def choice_usual_loop_st(self):
        self.appendF(FIRST_SET["<choice_usual_loop_st>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    302 <choice_usual_loop_st>	=>	<id_statements_choice_usual_loop>	<choice_usual_loop_st>    """
        if self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>"]:
            node_0 = self.id_statements_choice_usual_loop()
            node_1 = self.choice_usual_loop_st()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    303 <choice_usual_loop_st>	=>	<built_in_rec_call>	;	<choice_usual_loop_st>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>_1"]:
            node_0 = self.built_in_rec_call()
            token_1 = self.tokens[self.pos]
            self.parse_token(";")
            node_2 = self.choice_usual_loop_st()

            # Collect: [ExpressionStatement($0)] + $2
            result = [ExpressionStatement(node_0)] + node_2
            return result

            """    304 <choice_usual_loop_st>	=>	<conditional_st_loop>	<choice_usual_loop_st>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>_2"]:
            node_0 = self.conditional_st_loop()
            node_1 = self.choice_usual_loop_st()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    305 <choice_usual_loop_st>	=>	<looping_st>	<choice_usual_loop_st>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>_3"]:
            node_0 = self.looping_st()
            node_1 = self.choice_usual_loop_st()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    306 <choice_usual_loop_st>	=>	<jump_st>	<choice_usual_loop_st>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>_4"]:
            node_0 = self.jump_st()
            node_1 = self.choice_usual_loop_st()

            # Collect: [$0] + $1
            result = [node_0] + node_1
            return result

            """    307 <choice_usual_loop_st>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<choice_usual_loop_st>_5"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def id_statements_choice_usual_loop(self):
        self.appendF(FIRST_SET["<id_statements_choice_usual_loop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    308 <id_statements_choice_usual_loop>	=>	id	<id_statements_ext>	<choice_usual_loop_st>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_statements_choice_usual_loop>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.id_statements_ext()
            node_2 = self.choice_usual_loop_st()

            return node_1
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def jump_st(self):
        self.appendF(FIRST_SET["<jump_st>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    309 <jump_st>	=>	<jump_next>    """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_st>"]:
            node_0 = self.jump_next()

            return node_0

            """    310 <jump_st>	=>	<jump_stop>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<jump_st>_1"]:
            node_0 = self.jump_stop()

            return node_0

            """    311 <jump_st>	=>	<jump_serve>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<jump_st>_2"]:
            node_0 = self.jump_serve()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def jump_next(self):
        self.appendF(FIRST_SET["<jump_next>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    312 <jump_next>	=>	next	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_next>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("next")
            token_1 = self.tokens[self.pos]
            self.parse_token(";")

            # Create ContinueStatement node
            node = ContinueStatement(token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def jump_stop(self):
        self.appendF(FIRST_SET["<jump_stop>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    313 <jump_stop>	=>	stop	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_stop>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("stop")
            token_1 = self.tokens[self.pos]
            self.parse_token(";")

            # Create BreakStatement node
            node = BreakStatement(token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def jump_serve(self):
        self.appendF(FIRST_SET["<jump_serve>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    314 <jump_serve>	=>	serve	<value>	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<jump_serve>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("serve")
            node_1 = self.value()
            token_2 = self.tokens[self.pos]
            self.parse_token(";")

            # Create ServeStatement node
            node = ServeStatement(node_1, token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def loop_repeat(self):
        self.appendF(FIRST_SET["<loop_repeat>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    315 <loop_repeat>	=>	repeat	(	<strict_flag_expr>	)	<loop_platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_repeat>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("repeat")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_flag_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")
            node_4 = self.loop_platter()

            # Create RepeatLoop node
            node = RepeatLoop(node_2, node_4, token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def loop_order(self):
        self.appendF(FIRST_SET["<loop_order>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    316 <loop_order>	=>	order	<loop_platter>	repeat	(	<strict_flag_expr>	)	;    """
        if self.tokens[self.pos].type in PREDICT_SET["<loop_order>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("order")
            node_1 = self.loop_platter()
            token_2 = self.tokens[self.pos]
            self.parse_token("repeat")
            token_3 = self.tokens[self.pos]
            self.parse_token("(")
            node_4 = self.strict_flag_expr()
            token_5 = self.tokens[self.pos]
            self.parse_token(")")
            token_6 = self.tokens[self.pos]
            self.parse_token(";")

            # Create OrderRepeatLoop node
            node = OrderRepeatLoop(node_1, node_4, token_0.line, token_0.col)
            return node
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def usual_clause(self):
        self.appendF(FIRST_SET["<usual_clause>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    317 <usual_clause>	=>	usual	:	<statements_menu>    """
        if self.tokens[self.pos].type in PREDICT_SET["<usual_clause>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("usual")
            token_1 = self.tokens[self.pos]
            self.parse_token(":")
            node_2 = self.statements_menu()

            return node_2

            """    318 <usual_clause>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<usual_clause>_1"]:
            # Collect: []
            result = []
            return result


        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_chars_expr(self):
        self.appendF(FIRST_SET["<strict_chars_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    319 <strict_chars_expr>	=>	<strict_chars_factor>	<strict_chars_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_expr>"]:
            node_0 = self.strict_chars_factor()
            node_1 = self.strict_chars_add_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_chars_factor(self):
        self.appendF(FIRST_SET["<strict_chars_factor>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    320 <strict_chars_factor>	=>	<ret_chars>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_factor>"]:
            node_0 = self.ret_chars()

            return node_0

            """    321 <strict_chars_factor>	=>	<id>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_factor>_1"]:
            node_0 = self.id_()

            return node_0

            """    322 <strict_chars_factor>	=>	(	<strict_chars_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_factor>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("(")
            node_1 = self.strict_chars_expr()
            token_2 = self.tokens[self.pos]
            self.parse_token(")")

            return node_1

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_chars_add_tail(self):
        self.appendF(FIRST_SET["<strict_chars_add_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    323 <strict_chars_add_tail>	=>	+	<strict_chars_factor>	<strict_chars_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_chars_add_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("+")
            node_1 = self.strict_chars_factor()
            node_2 = self.strict_chars_add_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "+", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    324 <strict_chars_add_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_chars_add_tail>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_piece_expr(self):
        self.appendF(FIRST_SET["<strict_piece_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    325 <strict_piece_expr>	=>	<strict_piece_term>	<strict_piece_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_expr>"]:
            node_0 = self.strict_piece_term()
            node_1 = self.strict_piece_add_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_piece_term(self):
        self.appendF(FIRST_SET["<strict_piece_term>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    326 <strict_piece_term>	=>	<strict_piece_factor>	<strict_piece_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_term>"]:
            node_0 = self.strict_piece_factor()
            node_1 = self.strict_piece_mult_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_piece_factor(self):
        self.appendF(FIRST_SET["<strict_piece_factor>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    327 <strict_piece_factor>	=>	<ret_piece>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor>"]:
            node_0 = self.ret_piece()

            return node_0

            """    328 <strict_piece_factor>	=>	<id>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor>_1"]:
            node_0 = self.id_()

            return node_0

            """    329 <strict_piece_factor>	=>	(	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_factor>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("(")
            node_1 = self.strict_piece_expr()
            token_2 = self.tokens[self.pos]
            self.parse_token(")")

            return node_1

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_piece_mult_tail(self):
        self.appendF(FIRST_SET["<strict_piece_mult_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    330 <strict_piece_mult_tail>	=>	*	<strict_piece_factor>	<strict_piece_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("*")
            node_1 = self.strict_piece_factor()
            node_2 = self.strict_piece_mult_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "*", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    331 <strict_piece_mult_tail>	=>	/	<strict_piece_factor>	<strict_piece_mult_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("/")
            node_1 = self.strict_piece_factor()
            node_2 = self.strict_piece_mult_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "/", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    332 <strict_piece_mult_tail>	=>	%	<strict_piece_factor>	<strict_piece_mult_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("%")
            node_1 = self.strict_piece_factor()
            node_2 = self.strict_piece_mult_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "%", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    333 <strict_piece_mult_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_mult_tail>_3"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_piece_add_tail(self):
        self.appendF(FIRST_SET["<strict_piece_add_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    334 <strict_piece_add_tail>	=>	+	<strict_piece_term>	<strict_piece_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("+")
            node_1 = self.strict_piece_term()
            node_2 = self.strict_piece_add_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "+", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    335 <strict_piece_add_tail>	=>	-	<strict_piece_term>	<strict_piece_add_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("-")
            node_1 = self.strict_piece_term()
            node_2 = self.strict_piece_add_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "-", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    336 <strict_piece_add_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_add_tail>_2"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_sip_expr(self):
        self.appendF(FIRST_SET["<strict_sip_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    337 <strict_sip_expr>	=>	<strict_sip_term>	<strict_sip_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_expr>"]:
            node_0 = self.strict_sip_term()
            node_1 = self.strict_sip_add_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_sip_term(self):
        self.appendF(FIRST_SET["<strict_sip_term>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    338 <strict_sip_term>	=>	<strict_sip_factor>	<strict_sip_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_term>"]:
            node_0 = self.strict_sip_factor()
            node_1 = self.strict_sip_mult_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_sip_factor(self):
        self.appendF(FIRST_SET["<strict_sip_factor>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    339 <strict_sip_factor>	=>	<id>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_factor>"]:
            node_0 = self.id_()

            return node_0

            """    340 <strict_sip_factor>	=>	<ret_sip>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_factor>_1"]:
            node_0 = self.ret_sip()

            return node_0

            """    341 <strict_sip_factor>	=>	(	<strict_sip_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_factor>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("(")
            node_1 = self.strict_sip_expr()
            token_2 = self.tokens[self.pos]
            self.parse_token(")")

            return node_1

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_sip_mult_tail(self):
        self.appendF(FIRST_SET["<strict_sip_mult_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    342 <strict_sip_mult_tail>	=>	*	<strict_sip_factor>	<strict_sip_mult_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_mult_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("*")
            node_1 = self.strict_sip_factor()
            node_2 = self.strict_sip_mult_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "*", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    343 <strict_sip_mult_tail>	=>	/	<strict_sip_factor>	<strict_sip_mult_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_mult_tail>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("/")
            node_1 = self.strict_sip_factor()
            node_2 = self.strict_sip_mult_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "/", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    344 <strict_sip_mult_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_mult_tail>_2"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_sip_add_tail(self):
        self.appendF(FIRST_SET["<strict_sip_add_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    345 <strict_sip_add_tail>	=>	+	<strict_sip_term>	<strict_sip_add_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_sip_add_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("+")
            node_1 = self.strict_sip_term()
            node_2 = self.strict_sip_add_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "+", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    346 <strict_sip_add_tail>	=>	-	<strict_sip_term>	<strict_sip_add_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_add_tail>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("-")
            node_1 = self.strict_sip_term()
            node_2 = self.strict_sip_add_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "-", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    347 <strict_sip_add_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_sip_add_tail>_2"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def ret_flag(self):
        self.appendF(FIRST_SET["<ret_flag>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    348 <ret_flag>	=>	matches	(	<strict_datas_expr>	,	<strict_datas_expr>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_flag>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("matches")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_datas_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(",")
            node_4 = self.strict_datas_expr()
            token_5 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("matches", [node_2, node_4], token_0.line, token_0.col)
            return node

            """    349 <ret_flag>	=>	flag_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_flag>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("flag_lit")

            # Create Literal node
            node = Literal("flag", token_0.value, token_0.line, token_0.col)
            return node

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def ret_chars(self):
        self.appendF(FIRST_SET["<ret_chars>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    350 <ret_chars>	=>	bill	(	<strict_chars_expr>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_chars>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("bill")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_chars_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("bill", [node_2], token_0.line, token_0.col)
            return node

            """    351 <ret_chars>	=>	take	(	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("take")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            token_2 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("take", [], token_0.line, token_0.col)
            return node

            """    352 <ret_chars>	=>	copy	(	<strict_chars_expr>	,	<strict_piece_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("copy")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_chars_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(",")
            node_4 = self.strict_piece_expr()
            token_5 = self.tokens[self.pos]
            self.parse_token(",")
            node_6 = self.strict_piece_expr()
            token_7 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("copy", [node_2, node_4, node_6], token_0.line, token_0.col)
            return node

            """    353 <ret_chars>	=>	cut	(	<strict_sip_expr>	,	<strict_sip_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("cut")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_sip_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(",")
            node_4 = self.strict_sip_expr()
            token_5 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("cut", [node_2, node_4], token_0.line, token_0.col)
            return node

            """    354 <ret_chars>	=>	tochars	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("tochars")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.any_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("tochars", [node_2], token_0.line, token_0.col)
            return node

            """    355 <ret_chars>	=>	chars_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_chars>_5"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("chars_lit")

            # Create Literal node
            node = Literal("chars", token_0.value, token_0.line, token_0.col)
            return node

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def ret_piece(self):
        self.appendF(FIRST_SET["<ret_piece>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    356 <ret_piece>	=>	topiece	(	<any_expr>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_piece>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("topiece")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.any_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("topiece", [node_2], token_0.line, token_0.col)
            return node

            """    357 <ret_piece>	=>	size	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("size")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_array_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("size", [node_2], token_0.line, token_0.col)
            return node

            """    358 <ret_piece>	=>	search	(	<strict_array_expr>	,	<value>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("search")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_array_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(",")
            node_4 = self.value()
            token_5 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("search", [node_2, node_4], token_0.line, token_0.col)
            return node

            """    359 <ret_piece>	=>	fact	(	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("fact")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_piece_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("fact", [node_2], token_0.line, token_0.col)
            return node

            """    360 <ret_piece>	=>	pow	(	<strict_piece_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("pow")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_piece_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(",")
            node_4 = self.strict_piece_expr()
            token_5 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("pow", [node_2, node_4], token_0.line, token_0.col)
            return node

            """    361 <ret_piece>	=>	piece_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_piece>_5"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("piece_lit")

            # Create Literal node
            node = Literal("piece", token_0.value, token_0.line, token_0.col)
            return node

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def ret_sip(self):
        self.appendF(FIRST_SET["<ret_sip>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    362 <ret_sip>	=>	sqrt	(	<strict_piece_expr>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_sip>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("sqrt")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_piece_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("sqrt", [node_2], token_0.line, token_0.col)
            return node

            """    363 <ret_sip>	=>	rand	(	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_sip>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("rand")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            token_2 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("rand", [], token_0.line, token_0.col)
            return node

            """    364 <ret_sip>	=>	tosip	(	<any_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_sip>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("tosip")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.any_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("tosip", [node_2], token_0.line, token_0.col)
            return node

            """    365 <ret_sip>	=>	sip_lit    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_sip>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("sip_lit")

            # Create Literal node
            node = Literal("sip", token_0.value, token_0.line, token_0.col)
            return node

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def ret_array(self):
        self.appendF(FIRST_SET["<ret_array>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    366 <ret_array>	=>	append	(	<strict_array_expr>	,	<value>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<ret_array>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("append")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_array_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(",")
            node_4 = self.value()
            token_5 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("append", [node_2, node_4], token_0.line, token_0.col)
            return node

            """    367 <ret_array>	=>	sort	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_array>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("sort")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_array_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("sort", [node_2], token_0.line, token_0.col)
            return node

            """    368 <ret_array>	=>	reverse	(	<strict_array_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_array>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("reverse")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_array_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("reverse", [node_2], token_0.line, token_0.col)
            return node

            """    369 <ret_array>	=>	remove	(	<strict_array_expr>	,	<strict_piece_expr>	)    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ret_array>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("remove")
            token_1 = self.tokens[self.pos]
            self.parse_token("(")
            node_2 = self.strict_array_expr()
            token_3 = self.tokens[self.pos]
            self.parse_token(",")
            node_4 = self.strict_piece_expr()
            token_5 = self.tokens[self.pos]
            self.parse_token(")")

            # Create RecipeCall node
            node = RecipeCall("remove", [node_2, node_4], token_0.line, token_0.col)
            return node

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_datas_expr(self):
        self.appendF(FIRST_SET["<strict_datas_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    370 <strict_datas_expr>	=>	[	<notation_val>	]    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_datas_expr>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.notation_val()
            token_2 = self.tokens[self.pos]
            self.parse_token("]")

            # Create ArrayLiteral node
            node = ArrayLiteral(node_1, token_0.line, token_0.col)
            return node

            """    371 <strict_datas_expr>	=>	id	<id_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_datas_expr>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.id_tail()

            return Identifier(token_0.value, token_0.line, token_0.col)

            """    372 <strict_datas_expr>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_datas_expr>_2"]:
            node_0 = self.ret_array()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_array_expr(self):
        self.appendF(FIRST_SET["<strict_array_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    373 <strict_array_expr>	=>	[	<array_element_id>	]    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_array_expr>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("[")
            node_1 = self.array_element_id()
            token_2 = self.tokens[self.pos]
            self.parse_token("]")

            # Create ArrayLiteral node
            node = ArrayLiteral(node_1, token_0.line, token_0.col)
            return node

            """    374 <strict_array_expr>	=>	id	<id_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_array_expr>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.id_tail()

            return Identifier(token_0.value, token_0.line, token_0.col)

            """    375 <strict_array_expr>	=>	<ret_array>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_array_expr>_2"]:
            node_0 = self.ret_array()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def id_(self):
        self.appendF(FIRST_SET["<id>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    376 <id>	=>	id	<id_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("id")
            node_1 = self.id_tail()

            # Build accessor: id token with tail
            base = Identifier(token_0.value, token_0.line, token_0.col)
            if node_1:
                return node_1(base)
            else:
                return base
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def id_tail(self):
        self.appendF(FIRST_SET["<id_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    377 <id_tail>	=>	<call_tailopt>    """
        if self.tokens[self.pos].type in PREDICT_SET["<id_tail>"]:
            node_0 = self.call_tailopt()

            return node_0

            """    378 <id_tail>	=>	<accessor_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<id_tail>_1"]:
            node_0 = self.accessor_tail()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def call_tailopt(self):
        self.appendF(FIRST_SET["<call_tailopt>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    379 <call_tailopt>	=>	(	<flavor>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<call_tailopt>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("(")
            node_1 = self.flavor()
            token_2 = self.tokens[self.pos]
            self.parse_token(")")

            # Build function call closure
            def build_call(base):
                # Extract function name from Identifier node
                if hasattr(base, 'name'):
                    func_name = base.name
                else:
                    func_name = str(base)
            
                # Create RecipeCall node
                node = RecipeCall(func_name, node_1, token_0.line, token_0.col)
                return node
        
            return build_call

            """    380 <call_tailopt>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<call_tailopt>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def chars_ops(self):
        self.appendF(FIRST_SET["<chars_ops>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    381 <chars_ops>	=>	+    """
        if self.tokens[self.pos].type in PREDICT_SET["<chars_ops>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("+")

            return self.tokens[self.pos - 1].value
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def sip_ops(self):
        self.appendF(FIRST_SET["<sip_ops>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    382 <sip_ops>	=>	+    """
        if self.tokens[self.pos].type in PREDICT_SET["<sip_ops>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("+")

            return self.tokens[self.pos - 1].value

            """    383 <sip_ops>	=>	-    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_ops>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("-")

            return self.tokens[self.pos - 1].value

            """    384 <sip_ops>	=>	*    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_ops>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("*")

            return self.tokens[self.pos - 1].value

            """    385 <sip_ops>	=>	/    """
        elif self.tokens[self.pos].type in PREDICT_SET["<sip_ops>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("/")

            return self.tokens[self.pos - 1].value

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def all_ops(self):
        self.appendF(FIRST_SET["<all_ops>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    386 <all_ops>	=>	%    """
        if self.tokens[self.pos].type in PREDICT_SET["<all_ops>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("%")

            return self.tokens[self.pos - 1].value

            """    387 <all_ops>	=>	<sip_ops>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<all_ops>_1"]:
            node_0 = self.sip_ops()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def rel_op(self):
        self.appendF(FIRST_SET["<rel_op>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    388 <rel_op>	=>	==    """
        if self.tokens[self.pos].type in PREDICT_SET["<rel_op>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("==")

            return self.tokens[self.pos - 1].value

            """    389 <rel_op>	=>	!=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("!=")

            return self.tokens[self.pos - 1].value

            """    390 <rel_op>	=>	>=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(">=")

            return self.tokens[self.pos - 1].value

            """    391 <rel_op>	=>	<=    """
        elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("<=")

            return self.tokens[self.pos - 1].value

            """    392 <rel_op>	=>	<    """
        elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("<")

            return self.tokens[self.pos - 1].value

            """    393 <rel_op>	=>	>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<rel_op>_5"]:
            token_0 = self.tokens[self.pos]
            self.parse_token(">")

            return self.tokens[self.pos - 1].value

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_eq_tail(self):
        self.appendF(FIRST_SET["<flag_eq_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    394 <flag_eq_tail>	=>	==	<simple_flag>	<flag_eq_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_eq_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("==")
            node_1 = self.simple_flag()
            node_2 = self.flag_eq_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "==", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    395 <flag_eq_tail>	=>	!=	<simple_flag>	<flag_eq_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_eq_tail>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("!=")
            node_1 = self.simple_flag()
            node_2 = self.flag_eq_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "!=", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    396 <flag_eq_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_eq_tail>_2"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_op_tail(self):
        self.appendF(FIRST_SET["<flag_op_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    397 <flag_op_tail>	=>	<flag_eq_tail>	<flag_expr_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_op_tail>"]:
            node_0 = self.flag_eq_tail()
            node_1 = self.flag_expr_tail()

            # Manual code
            return (lambda eq_tail, expr_tail: (lambda left: expr_tail(eq_tail(left))) if (eq_tail and expr_tail) else (expr_tail if expr_tail else eq_tail))(node_0, node_1)

            """    398 <flag_op_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_op_tail>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def cont_sip(self):
        self.appendF(FIRST_SET["<cont_sip>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    399 <cont_sip>	=>	<sip_ops>	<strict_sip_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<cont_sip>"]:
            node_0 = self.sip_ops()
            node_1 = self.strict_sip_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, node_0, node_1, None, None)
                return node
            return build_op

            """    400 <cont_sip>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<cont_sip>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def cont_piece(self):
        self.appendF(FIRST_SET["<cont_piece>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    401 <cont_piece>	=>	<all_ops>	<strict_piece_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<cont_piece>"]:
            node_0 = self.all_ops()
            node_1 = self.strict_piece_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, node_0, node_1, None, None)
                return node
            return build_op

            """    402 <cont_piece>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<cont_piece>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def cont_chars(self):
        self.appendF(FIRST_SET["<cont_chars>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    403 <cont_chars>	=>	<chars_ops>	<strict_chars_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<cont_chars>"]:
            node_0 = self.chars_ops()
            node_1 = self.strict_chars_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, node_0, node_1, None, None)
                return node
            return build_op

            """    404 <cont_chars>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<cont_chars>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_flag_expr(self):
        self.appendF(FIRST_SET["<strict_flag_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    405 <strict_flag_expr>	=>	<flag_operand>	<flag_expr_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_flag_expr>"]:
            node_0 = self.flag_operand()
            node_1 = self.flag_expr_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0
        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_expr_tail(self):
        self.appendF(FIRST_SET["<flag_expr_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    406 <flag_expr_tail>	=>	and	<strict_flag_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_expr_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("and")
            node_1 = self.strict_flag_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "and", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    407 <flag_expr_tail>	=>	or	<strict_flag_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_expr_tail>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("or")
            node_1 = self.strict_flag_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "or", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    408 <flag_expr_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_expr_tail>_2"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def simple_flag(self):
        self.appendF(FIRST_SET["<simple_flag>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    409 <simple_flag>	=>	(	<flag_operand>	)    """
        if self.tokens[self.pos].type in PREDICT_SET["<simple_flag>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("(")
            node_1 = self.flag_operand()
            token_2 = self.tokens[self.pos]
            self.parse_token(")")

            return node_1

            """    410 <simple_flag>	=>	<ret_flag>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<simple_flag>_1"]:
            node_0 = self.ret_flag()

            return node_0

            """    411 <simple_flag>	=>	<id>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<simple_flag>_2"]:
            node_0 = self.id_()

            return node_0

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_operand(self):
        self.appendF(FIRST_SET["<flag_operand>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    412 <flag_operand>	=>	<ret_piece>	<cont_piece>	<rel_op>	<strict_piece_expr>	<flag_eq_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_operand>"]:
            node_0 = self.ret_piece()
            node_1 = self.cont_piece()
            node_2 = self.rel_op()
            node_3 = self.strict_piece_expr()
            node_4 = self.flag_eq_tail()

            # Build binary operation: first apply arithmetic continuation, then relational op
            left = node_1(node_0) if node_1 else node_0
            result = BinaryOp(left, node_2, node_3, None, None)
            if node_4:
                return node_4(result)
            else:
                return result

            """    413 <flag_operand>	=>	<ret_sip>	<cont_sip>	<rel_op>	<strict_sip_expr>	<flag_eq_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_operand>_1"]:
            node_0 = self.ret_sip()
            node_1 = self.cont_sip()
            node_2 = self.rel_op()
            node_3 = self.strict_sip_expr()
            node_4 = self.flag_eq_tail()

            # Build binary operation: first apply arithmetic continuation, then relational op
            left = node_1(node_0) if node_1 else node_0
            result = BinaryOp(left, node_2, node_3, None, None)
            if node_4:
                return node_4(result)
            else:
                return result

            """    414 <flag_operand>	=>	<ret_flag>	<flag_eq_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_operand>_2"]:
            node_0 = self.ret_flag()
            node_1 = self.flag_eq_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    415 <flag_operand>	=>	<ret_chars>	<cont_chars>	<rel_op>	<strict_chars_expr>	<flag_eq_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_operand>_3"]:
            node_0 = self.ret_chars()
            node_1 = self.cont_chars()
            node_2 = self.rel_op()
            node_3 = self.strict_chars_expr()
            node_4 = self.flag_eq_tail()

            # Build binary operation: first apply arithmetic continuation, then relational op
            left = node_1(node_0) if node_1 else node_0
            result = BinaryOp(left, node_2, node_3, None, None)
            if node_4:
                return node_4(result)
            else:
                return result

            """    416 <flag_operand>	=>	not	<flag_operand>	<flag_eq_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_operand>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("not")
            node_1 = self.flag_operand()
            node_2 = self.flag_eq_tail()

            # Build unary operation
            node = UnaryOp("not", node_1, token_0.line, token_0.col)
            if node_2:
                return node_2(node)
            else:
                return node

            """    417 <flag_operand>	=>	<id>	<flag_cont_any>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_operand>_5"]:
            node_0 = self.id_()
            node_1 = self.flag_cont_any()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    418 <flag_operand>	=>	(	<any_expr>	)	<flag_cont_any>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_operand>_6"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("(")
            node_1 = self.any_expr()
            token_2 = self.tokens[self.pos]
            self.parse_token(")")
            node_3 = self.flag_cont_any()

            # Build binary operation: combine left with right tail
            if node_3:
                return node_3(node_1)
            else:
                return node_1

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_cont_any(self):
        self.appendF(FIRST_SET["<flag_cont_any>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    419 <flag_cont_any>	=>	+	<flag_cps_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_cont_any>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("+")
            node_1 = self.flag_cps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "+", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    420 <flag_cont_any>	=>	-	<flag_ps_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_cont_any>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("-")
            node_1 = self.flag_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "-", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    421 <flag_cont_any>	=>	*	<flag_ps_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_cont_any>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("*")
            node_1 = self.flag_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "*", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    422 <flag_cont_any>	=>	/	<flag_ps_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_cont_any>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("/")
            node_1 = self.flag_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "/", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    423 <flag_cont_any>	=>	%	<strict_piece_expr>	<rel_op>	<strict_piece_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_cont_any>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("%")
            node_1 = self.strict_piece_expr()
            node_2 = self.rel_op()
            node_3 = self.strict_piece_expr()

            # Manual code
            return lambda left: BinaryOp(BinaryOp(left, "%", node_1), node_2, node_3)

            """    424 <flag_cont_any>	=>	<rel_op>	<any_expr>	<flag_eq_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_cont_any>_5"]:
            node_0 = self.rel_op()
            node_1 = self.any_expr()
            node_2 = self.flag_eq_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, node_0, node_1, None, None)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    425 <flag_cont_any>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_cont_any>_6"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_cps_expr(self):
        self.appendF(FIRST_SET["<flag_cps_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    426 <flag_cps_expr>	=>	<ret_piece>	<cont_piece>	<rel_op>	<strict_piece_expr>	<flag_eq_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_cps_expr>"]:
            node_0 = self.ret_piece()
            node_1 = self.cont_piece()
            node_2 = self.rel_op()
            node_3 = self.strict_piece_expr()
            node_4 = self.flag_eq_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    427 <flag_cps_expr>	=>	<ret_sip>	<cont_sip>	<rel_op>	<strict_sip_expr>	<flag_eq_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_cps_expr>_1"]:
            node_0 = self.ret_sip()
            node_1 = self.cont_sip()
            node_2 = self.rel_op()
            node_3 = self.strict_sip_expr()
            node_4 = self.flag_eq_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    428 <flag_cps_expr>	=>	<ret_chars>	<cont_chars>	<rel_op>	<strict_chars_expr>	<flag_eq_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_cps_expr>_2"]:
            node_0 = self.ret_chars()
            node_1 = self.cont_chars()
            node_2 = self.rel_op()
            node_3 = self.strict_chars_expr()
            node_4 = self.flag_eq_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    429 <flag_cps_expr>	=>	<id>	<flag_cps_cont_any>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_cps_expr>_3"]:
            node_0 = self.id_()
            node_1 = self.flag_cps_cont_any()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    430 <flag_cps_expr>	=>	(	<any_expr>	)	<flag_cps_cont_any>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_cps_expr>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("(")
            node_1 = self.any_expr()
            token_2 = self.tokens[self.pos]
            self.parse_token(")")
            node_3 = self.flag_cps_cont_any()

            # Build binary operation: combine left with right tail
            if node_3:
                return node_3(node_1)
            else:
                return node_1

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_cps_cont_any(self):
        self.appendF(FIRST_SET["<flag_cps_cont_any>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    431 <flag_cps_cont_any>	=>	+	<flag_cps_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_cps_cont_any>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("+")
            node_1 = self.flag_cps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "+", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    432 <flag_cps_cont_any>	=>	-	<flag_ps_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_cps_cont_any>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("-")
            node_1 = self.flag_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "-", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    433 <flag_cps_cont_any>	=>	*	<flag_ps_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_cps_cont_any>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("*")
            node_1 = self.flag_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "*", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    434 <flag_cps_cont_any>	=>	/	<flag_ps_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_cps_cont_any>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("/")
            node_1 = self.flag_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "/", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    435 <flag_cps_cont_any>	=>	%	<strict_piece_expr>	<rel_op>	<strict_piece_expr>	<flag_eq_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_cps_cont_any>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("%")
            node_1 = self.strict_piece_expr()
            node_2 = self.rel_op()
            node_3 = self.strict_piece_expr()
            node_4 = self.flag_eq_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "%", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    436 <flag_cps_cont_any>	=>	<rel_op>	<strict_cps_expr>	<flag_eq_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_cps_cont_any>_5"]:
            node_0 = self.rel_op()
            node_1 = self.strict_cps_expr()
            node_2 = self.flag_eq_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, node_0, node_1, None, None)
                if node_2:
                    return node_2(node)
                return node
            return build_op

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_ps_expr(self):
        self.appendF(FIRST_SET["<flag_ps_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    437 <flag_ps_expr>	=>	<ret_piece>	<cont_piece>	<rel_op>	<strict_piece_expr>	<flag_eq_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_ps_expr>"]:
            node_0 = self.ret_piece()
            node_1 = self.cont_piece()
            node_2 = self.rel_op()
            node_3 = self.strict_piece_expr()
            node_4 = self.flag_eq_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    438 <flag_ps_expr>	=>	<ret_sip>	<cont_sip>	<rel_op>	<strict_sip_expr>	<flag_eq_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_ps_expr>_1"]:
            node_0 = self.ret_sip()
            node_1 = self.cont_sip()
            node_2 = self.rel_op()
            node_3 = self.strict_sip_expr()
            node_4 = self.flag_eq_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    439 <flag_ps_expr>	=>	<id>	<flag_ps_cont_any>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_ps_expr>_2"]:
            node_0 = self.id_()
            node_1 = self.flag_ps_cont_any()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    440 <flag_ps_expr>	=>	(	<any_expr>	)	<flag_ps_cont_any>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_ps_expr>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("(")
            node_1 = self.any_expr()
            token_2 = self.tokens[self.pos]
            self.parse_token(")")
            node_3 = self.flag_ps_cont_any()

            # Build binary operation: combine left with right tail
            if node_3:
                return node_3(node_1)
            else:
                return node_1

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def flag_ps_cont_any(self):
        self.appendF(FIRST_SET["<flag_ps_cont_any>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    441 <flag_ps_cont_any>	=>	+	<flag_ps_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<flag_ps_cont_any>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("+")
            node_1 = self.flag_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "+", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    442 <flag_ps_cont_any>	=>	-	<flag_ps_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_ps_cont_any>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("-")
            node_1 = self.flag_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "-", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    443 <flag_ps_cont_any>	=>	*	<flag_ps_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_ps_cont_any>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("*")
            node_1 = self.flag_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "*", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    444 <flag_ps_cont_any>	=>	/	<flag_ps_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_ps_cont_any>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("/")
            node_1 = self.flag_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "/", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    445 <flag_ps_cont_any>	=>	%	<strict_piece_expr>	<rel_op>	<strict_piece_expr>	<flag_eq_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_ps_cont_any>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("%")
            node_1 = self.strict_piece_expr()
            node_2 = self.rel_op()
            node_3 = self.strict_piece_expr()
            node_4 = self.flag_eq_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "%", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    446 <flag_ps_cont_any>	=>	<rel_op>	<strict_ps_expr>	<flag_eq_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<flag_ps_cont_any>_5"]:
            node_0 = self.rel_op()
            node_1 = self.strict_ps_expr()
            node_2 = self.flag_eq_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, node_0, node_1, None, None)
                if node_2:
                    return node_2(node)
                return node
            return build_op

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def any_expr(self):
        self.appendF(FIRST_SET["<any_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    447 <any_expr>	=>	<ret_piece>	<cont_piece>	<any_cont_p_flag_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<any_expr>"]:
            node_0 = self.ret_piece()
            node_1 = self.cont_piece()
            node_2 = self.any_cont_p_flag_tail()

            # Build binary operation: first apply arithmetic, then relational/logical
            left = node_1(node_0) if node_1 else node_0
            if node_2:
                return node_2(left)
            else:
                return left

            """    448 <any_expr>	=>	<ret_sip>	<cont_sip>	<any_cont_s_flag_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_1"]:
            node_0 = self.ret_sip()
            node_1 = self.cont_sip()
            node_2 = self.any_cont_s_flag_tail()

            # Build binary operation: first apply arithmetic, then relational/logical
            left = node_1(node_0) if node_1 else node_0
            if node_2:
                return node_2(left)
            else:
                return left

            """    449 <any_expr>	=>	<ret_flag>	<flag_op_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_2"]:
            node_0 = self.ret_flag()
            node_1 = self.flag_op_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    450 <any_expr>	=>	<ret_chars>	<cont_chars>	<any_cont_c_flag_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_3"]:
            node_0 = self.ret_chars()
            node_1 = self.cont_chars()
            node_2 = self.any_cont_c_flag_tail()

            # Build binary operation: first apply arithmetic, then relational/logical
            left = node_1(node_0) if node_1 else node_0
            if node_2:
                return node_2(left)
            else:
                return left

            """    451 <any_expr>	=>	<id>	<any_cont_any>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_4"]:
            node_0 = self.id_()
            node_1 = self.any_cont_any()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    452 <any_expr>	=>	(	<any_expr>	)	<any_cont_any>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_5"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("(")
            node_1 = self.any_expr()
            token_2 = self.tokens[self.pos]
            self.parse_token(")")
            node_3 = self.any_cont_any()

            # Build binary operation: combine left with right tail
            if node_3:
                return node_3(node_1)
            else:
                return node_1

            """    453 <any_expr>	=>	not	<strict_flag_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_expr>_6"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("not")
            node_1 = self.strict_flag_expr()

            # Create UnaryOp node
            node = UnaryOp("not", node_1, token_0.line, token_0.col)
            return node

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def any_cont_any(self):
        self.appendF(FIRST_SET["<any_cont_any>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    454 <any_cont_any>	=>	+	<strict_cps_expr>	<any_cont_cps_flag_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<any_cont_any>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("+")
            node_1 = self.strict_cps_expr()
            node_2 = self.any_cont_cps_flag_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "+", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    455 <any_cont_any>	=>	-	<strict_ps_expr>	<any_cont_ps_flag_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_cont_any>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("-")
            node_1 = self.strict_ps_expr()
            node_2 = self.any_cont_ps_flag_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "-", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    456 <any_cont_any>	=>	*	<strict_ps_expr>	<any_cont_ps_flag_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_cont_any>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("*")
            node_1 = self.strict_ps_expr()
            node_2 = self.any_cont_ps_flag_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "*", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    457 <any_cont_any>	=>	/	<strict_ps_expr>	<any_cont_ps_flag_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_cont_any>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("/")
            node_1 = self.strict_ps_expr()
            node_2 = self.any_cont_ps_flag_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "/", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    458 <any_cont_any>	=>	%	<strict_piece_expr>	<any_cont_p_flag_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_cont_any>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("%")
            node_1 = self.strict_piece_expr()
            node_2 = self.any_cont_p_flag_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "%", node_1, token_0.line, token_0.col)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    459 <any_cont_any>	=>	<rel_op>	<any_expr>	<flag_op_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_cont_any>_5"]:
            node_0 = self.rel_op()
            node_1 = self.any_expr()
            node_2 = self.flag_op_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, node_0, node_1, None, None)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    460 <any_cont_any>	=>	<flag_expr_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_cont_any>_6"]:
            node_0 = self.flag_expr_tail()

            return node_0

            """    461 <any_cont_any>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_cont_any>_7"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def any_cont_cps_flag_tail(self):
        self.appendF(FIRST_SET["<any_cont_cps_flag_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    462 <any_cont_cps_flag_tail>	=>	<rel_op>	<strict_cps_expr>	<flag_op_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<any_cont_cps_flag_tail>"]:
            node_0 = self.rel_op()
            node_1 = self.strict_cps_expr()
            node_2 = self.flag_op_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, node_0, node_1, None, None)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    463 <any_cont_cps_flag_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_cont_cps_flag_tail>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def any_cont_ps_flag_tail(self):
        self.appendF(FIRST_SET["<any_cont_ps_flag_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    464 <any_cont_ps_flag_tail>	=>	<rel_op>	<strict_ps_expr>	<flag_op_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<any_cont_ps_flag_tail>"]:
            node_0 = self.rel_op()
            node_1 = self.strict_ps_expr()
            node_2 = self.flag_op_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, node_0, node_1, None, None)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    465 <any_cont_ps_flag_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_cont_ps_flag_tail>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def any_cont_p_flag_tail(self):
        self.appendF(FIRST_SET["<any_cont_p_flag_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    466 <any_cont_p_flag_tail>	=>	<rel_op>	<strict_piece_expr>	<flag_op_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<any_cont_p_flag_tail>"]:
            node_0 = self.rel_op()
            node_1 = self.strict_piece_expr()
            node_2 = self.flag_op_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, node_0, node_1, None, None)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    467 <any_cont_p_flag_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_cont_p_flag_tail>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def any_cont_s_flag_tail(self):
        self.appendF(FIRST_SET["<any_cont_s_flag_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    468 <any_cont_s_flag_tail>	=>	<rel_op>	<strict_sip_expr>	<flag_op_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<any_cont_s_flag_tail>"]:
            node_0 = self.rel_op()
            node_1 = self.strict_sip_expr()
            node_2 = self.flag_op_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, node_0, node_1, None, None)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    469 <any_cont_s_flag_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_cont_s_flag_tail>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def any_cont_c_flag_tail(self):
        self.appendF(FIRST_SET["<any_cont_c_flag_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    470 <any_cont_c_flag_tail>	=>	<rel_op>	<strict_chars_expr>	<flag_op_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<any_cont_c_flag_tail>"]:
            node_0 = self.rel_op()
            node_1 = self.strict_chars_expr()
            node_2 = self.flag_op_tail()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, node_0, node_1, None, None)
                if node_2:
                    return node_2(node)
                return node
            return build_op

            """    471 <any_cont_c_flag_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<any_cont_c_flag_tail>_1"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_cps_expr(self):
        self.appendF(FIRST_SET["<strict_cps_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    472 <strict_cps_expr>	=>	<ret_piece>	<cont_piece>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_cps_expr>"]:
            node_0 = self.ret_piece()
            node_1 = self.cont_piece()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    473 <strict_cps_expr>	=>	<ret_sip>	<cont_sip>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_cps_expr>_1"]:
            node_0 = self.ret_sip()
            node_1 = self.cont_sip()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    474 <strict_cps_expr>	=>	<ret_chars>	<cont_chars>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_cps_expr>_2"]:
            node_0 = self.ret_chars()
            node_1 = self.cont_chars()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    475 <strict_cps_expr>	=>	<id>	<cps_cont_any>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_cps_expr>_3"]:
            node_0 = self.id_()
            node_1 = self.cps_cont_any()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    476 <strict_cps_expr>	=>	(	<strict_cps_expr>	)	<cps_cont_any>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_cps_expr>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("(")
            node_1 = self.strict_cps_expr()
            token_2 = self.tokens[self.pos]
            self.parse_token(")")
            node_3 = self.cps_cont_any()

            # Build binary operation: combine left with right tail
            if node_3:
                return node_3(node_1)
            else:
                return node_1

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def cps_cont_any(self):
        self.appendF(FIRST_SET["<cps_cont_any>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    477 <cps_cont_any>	=>	+	<strict_cps_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<cps_cont_any>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("+")
            node_1 = self.strict_cps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "+", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    478 <cps_cont_any>	=>	-	<strict_ps_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<cps_cont_any>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("-")
            node_1 = self.strict_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "-", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    479 <cps_cont_any>	=>	*	<strict_ps_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<cps_cont_any>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("*")
            node_1 = self.strict_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "*", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    480 <cps_cont_any>	=>	/	<strict_ps_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<cps_cont_any>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("/")
            node_1 = self.strict_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "/", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    481 <cps_cont_any>	=>	%	<strict_piece_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<cps_cont_any>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("%")
            node_1 = self.strict_piece_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "%", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    482 <cps_cont_any>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<cps_cont_any>_5"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_ps_expr(self):
        self.appendF(FIRST_SET["<strict_ps_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    483 <strict_ps_expr>	=>	<ret_piece>	<cont_piece>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_ps_expr>"]:
            node_0 = self.ret_piece()
            node_1 = self.cont_piece()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    484 <strict_ps_expr>	=>	<ret_sip>	<cont_sip>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_ps_expr>_1"]:
            node_0 = self.ret_sip()
            node_1 = self.cont_sip()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    485 <strict_ps_expr>	=>	<id>	<ps_cont_any>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_ps_expr>_2"]:
            node_0 = self.id_()
            node_1 = self.ps_cont_any()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    486 <strict_ps_expr>	=>	(	<strict_ps_expr>	)	<ps_cont_any>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_ps_expr>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("(")
            node_1 = self.strict_ps_expr()
            token_2 = self.tokens[self.pos]
            self.parse_token(")")
            node_3 = self.ps_cont_any()

            # Build binary operation: combine left with right tail
            if node_3:
                return node_3(node_1)
            else:
                return node_1

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def ps_cont_any(self):
        self.appendF(FIRST_SET["<ps_cont_any>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    487 <ps_cont_any>	=>	+	<strict_ps_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<ps_cont_any>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("+")
            node_1 = self.strict_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "+", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    488 <ps_cont_any>	=>	-	<strict_ps_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ps_cont_any>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("-")
            node_1 = self.strict_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "-", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    489 <ps_cont_any>	=>	*	<strict_ps_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ps_cont_any>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("*")
            node_1 = self.strict_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "*", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    490 <ps_cont_any>	=>	/	<strict_ps_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ps_cont_any>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("/")
            node_1 = self.strict_ps_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "/", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    491 <ps_cont_any>	=>	%	<strict_piece_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ps_cont_any>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("%")
            node_1 = self.strict_piece_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "%", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    492 <ps_cont_any>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<ps_cont_any>_5"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

    def strict_piece_chars_expr(self):
        self.appendF(FIRST_SET["<strict_piece_chars_expr>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    493 <strict_piece_chars_expr>	=>	<id>	<pc_ambig_tail>    """
        if self.tokens[self.pos].type in PREDICT_SET["<strict_piece_chars_expr>"]:
            node_0 = self.id_()
            node_1 = self.pc_ambig_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    494 <strict_piece_chars_expr>	=>	<ret_piece>	<strict_piece_mult_tail>	<strict_piece_add_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_chars_expr>_1"]:
            node_0 = self.ret_piece()
            node_1 = self.strict_piece_mult_tail()
            node_2 = self.strict_piece_add_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    495 <strict_piece_chars_expr>	=>	<ret_chars>	<strict_chars_add_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_chars_expr>_2"]:
            node_0 = self.ret_chars()
            node_1 = self.strict_chars_add_tail()

            # Build binary operation: combine left with right tail
            if node_1:
                return node_1(node_0)
            else:
                return node_0

            """    496 <strict_piece_chars_expr>	=>	(	<strict_piece_chars_expr>	)	<pc_ambig_tail>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<strict_piece_chars_expr>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("(")
            node_1 = self.strict_piece_chars_expr()
            token_2 = self.tokens[self.pos]
            self.parse_token(")")
            node_3 = self.pc_ambig_tail()

            # Build binary operation: combine left with right tail
            if node_3:
                return node_3(node_1)
            else:
                return node_1

        else: self.parse_token(self.error_arr)

        log.info("Exit: " + self.tokens[self.pos].type)

    def pc_ambig_tail(self):
        self.appendF(FIRST_SET["<pc_ambig_tail>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    497 <pc_ambig_tail>	=>	+	<strict_piece_chars_expr>    """
        if self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_tail>"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("+")
            node_1 = self.strict_piece_chars_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "+", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    498 <pc_ambig_tail>	=>	-	<strict_piece_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_tail>_1"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("-")
            node_1 = self.strict_piece_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "-", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    499 <pc_ambig_tail>	=>	*	<strict_piece_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_tail>_2"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("*")
            node_1 = self.strict_piece_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "*", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    500 <pc_ambig_tail>	=>	/	<strict_piece_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_tail>_3"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("/")
            node_1 = self.strict_piece_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "/", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    501 <pc_ambig_tail>	=>	%	<strict_piece_expr>    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_tail>_4"]:
            token_0 = self.tokens[self.pos]
            self.parse_token("%")
            node_1 = self.strict_piece_expr()

            # Build binary operation chain
            def build_op(left):
                node = BinaryOp(left, "%", node_1, token_0.line, token_0.col)
                return node
            return build_op

            """    502 <pc_ambig_tail>	=>	    """
        elif self.tokens[self.pos].type in PREDICT_SET["<pc_ambig_tail>_5"]:
            return None


        log.info("Exit: " + self.tokens[self.pos].type)

