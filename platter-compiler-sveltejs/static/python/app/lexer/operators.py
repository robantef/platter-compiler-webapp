from app.lexer.token import Token
from app.lexer.protocol import LexerProtocol


class LexerOperators(LexerProtocol):

    def s201(self):  # +
        self.advance()
        if self.current == "=": return self.s203()
        if self._match_delimiter(self.op1_dlm): return self.s202()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s202(self):  # + (Accepting State 202)
        return Token("+", "+", self.start_line, self.start_col)

    def s203(self):  # +=
        self.advance()
        if self._match_delimiter(self.op1_dlm): return self.s204()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s204(self):  # += (Accepting State 204)
        return Token("+=", "+=", self.start_line, self.start_col)

    def s205(self):  # -
        self.advance()
        if self._match_delimiter(self.op2_dlm): return self.s206()
        if self.current == "=": return self.s207()
        if self.current == "0": return self.s307()
        if self.current in self.numeric: return self.s309()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s206(self):  # - (Accepting State 206)
        return Token("-", "-", self.start_line, self.start_col)

    def s207(self):  # -=
        self.advance()
        if self._match_delimiter(self.op1_dlm): return self.s208()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s208(self):  # -= (Accepting State 208)
        return Token("-=", "-=", self.start_line, self.start_col)

    def s209(self):  # *
        self.advance()
        if self.current == "=": return self.s211()
        if self._match_delimiter(self.op1_dlm): return self.s210()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s210(self):  # * (Accepting State 210)
        return Token("*", "*", self.start_line, self.start_col)

    def s211(self):  # *=
        self.advance()
        if self._match_delimiter(self.op1_dlm): return self.s212()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s212(self):  # *= (Accepting State 212)
        return Token("*=", "*=", self.start_line, self.start_col)

    def s213(self):  # /
        self.advance()
        if self.current == "=": return self.s215()
        if self._match_delimiter(self.op1_dlm): return self.s214()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s214(self):  # / (Accepting State 214)
        return Token("/", "/", self.start_line, self.start_col)

    def s215(self):  # /=
        self.advance()
        if self._match_delimiter(self.op1_dlm): return self.s216()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s216(self):  # /= (Accepting State 216)
        return Token("/=", "/=", self.start_line, self.start_col)

    def s217(self):  # %
        self.advance()
        if self.current == "=": return self.s219()
        if self._match_delimiter(self.op1_dlm): return self.s218()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s218(self):  # % (Accepting State 218)
        return Token("%", "%", self.start_line, self.start_col)

    def s219(self):  # %=
        self.advance()
        if self._match_delimiter(self.op1_dlm): return self.s220()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s220(self):  # %= (Accepting State 220)
        return Token("%=", "%=", self.start_line, self.start_col)

    def s221(self):  # >
        self.advance()
        if self.current == "=": return self.s223()
        if self._match_delimiter(self.op1_dlm): return self.s222()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s222(self):  # > (Accepting State 222)
        return Token(">", ">", self.start_line, self.start_col)

    def s223(self):  # >=
        self.advance()
        if self._match_delimiter(self.op1_dlm): return self.s224()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s224(self):  # >= (Accepting State 224)
        return Token(">=", ">=", self.start_line, self.start_col)

    def s225(self):  # <
        self.advance()
        if self.current == "=": return self.s227()
        if self._match_delimiter(self.op1_dlm): return self.s226()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s226(self):  # < (Accepting State 226)
        return Token("<", "<", self.start_line, self.start_col)

    def s227(self):  # <=
        self.advance()
        if self._match_delimiter(self.op1_dlm): return self.s228()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s228(self):  # <= (Accepting State 228)
        return Token("<=", "<=", self.start_line, self.start_col)

    def s229(self):  # =
        self.advance()
        if self.current == "=": return self.s231()
        if self._match_delimiter(self.equal_dlm): return self.s230()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s230(self):  # = (Accepting State 230)
        return Token("=", "=", self.start_line, self.start_col)

    def s231(self):  # ==
        self.advance()
        if self._match_delimiter(self.op1_dlm): return self.s232()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s232(self):  # == (Accepting State 232)
        return Token("==", "==", self.start_line, self.start_col)

    def s233(self):  # !
        self.advance()
        if self.current == "=": return self.s234()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s234(self):  # !=
        self.advance()
        if self._match_delimiter(self.op1_dlm): return self.s235()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s235(self):  # != (Accepting State 235)
        return Token("!=", "!=", self.start_line, self.start_col)

    # --- Symbols ---
    def s236(self):  # space (Accepting State 236)
        self.advance()
        return Token("space", "space", self.start_line, self.start_col)

    def s237(self):  # tab (Accepting State 237)
        self.advance()
        return Token("tab", "tab", self.start_line, self.start_col)

    def s238(self):  # newline (Accepting State 238)
        self.advance()
        return Token("newline", "newline", self.start_line, self.start_col)

    def s239(self): 
        self.advance()
        if self._match_delimiter(self.dlm_1): return self.s240()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s240(self): 
        return Token(",", ",", self.start_line, self.start_col)

    def s241(self): 
        self.advance()
        if self._match_delimiter(self.dlm_2): return self.s242()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s242(self): 
        return Token(":", ":", self.start_line, self.start_col)

    def s243(self): 
        self.advance()
        if self._match_delimiter(self.dlm_3): return self.s244()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s244(self): 
        return Token(";", ";", self.start_line, self.start_col)

    def s245(self):  
        self.advance()
        if self._match_delimiter(self.dlm_4): return self.s246()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s246(self):
        return Token("(", "(", self.start_line, self.start_col)

    def s247(self): 
        self.advance()
        if self._match_delimiter(self.dlm_5): return self.s248()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s248(self): 
        return Token(")", ")", self.start_line, self.start_col)

    def s249(self): 
        self.advance()
        if self._match_delimiter(self.dlm_6): return self.s250()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s250(self): 
        return Token("[", "[", self.start_line, self.start_col)

    def s251(self): 
        self.advance()
        if self._match_delimiter(self.dlm_7): return self.s252()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s252(self): 
        return Token("]", "]", self.start_line, self.start_col)

    def s253(self):  
        self.advance()
        if self._match_delimiter(self.dlm_8): return self.s254()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s254(self):
        return Token("{", "{", self.start_line, self.start_col)

    def s255(self): 
        self.advance()
        if self._match_delimiter(self.dlm_9): return self.s256()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s256(self):  
        return Token("}", "}", self.start_line, self.start_col)
