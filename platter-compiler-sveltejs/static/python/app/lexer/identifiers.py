from app.lexer.token import Token
from app.lexer.protocol import LexerProtocol


class LexerIdentifier(LexerProtocol):
    def s257(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s258()
        if self.current in self.id_chars: return self.s259()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s258(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s259(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s260()
        if self.current in self.id_chars: return self.s261()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s260(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s261(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s262()
        if self.current in self.id_chars: return self.s263()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s262(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s263(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s264()
        if self.current in self.id_chars: return self.s265()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s264(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s265(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s266()
        if self.current in self.id_chars: return self.s267()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s266(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s267(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s268()
        if self.current in self.id_chars: return self.s269()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s268(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s269(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s270()
        if self.current in self.id_chars: return self.s271()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s270(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s271(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s272()
        if self.current in self.id_chars: return self.s273()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s272(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s273(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s274()
        if self.current in self.id_chars: return self.s275()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s274(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s275(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s276()
        if self.current in self.id_chars: return self.s277()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s276(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s277(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s278()
        if self.current in self.id_chars: return self.s279()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s278(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s279(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s280()
        if self.current in self.id_chars: return self.s281()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s280(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s281(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s282()
        if self.current in self.id_chars: return self.s283()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s282(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s283(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s284()
        if self.current in self.id_chars: return self.s285()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s284(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s285(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s286()
        if self.current in self.id_chars: return self.s287()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s286(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s287(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s288()
        if self.current in self.id_chars: return self.s289()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s288(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s289(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s290()
        if self.current in self.id_chars: return self.s291()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s290(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s291(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s292()
        if self.current in self.id_chars: return self.s293()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s292(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s293(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s294()
        if self.current in self.id_chars: return self.s295()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s294(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s295(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s296()
        if self.current in self.id_chars: return self.s297()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s296(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s297(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s298()
        if self.current in self.id_chars: return self.s299()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s298(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s299(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s300()
        if self.current in self.id_chars: return self.s301()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s300(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s301(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s302()
        if self.current in self.id_chars: return self.s303()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s302(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s303(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s304()
        if self.current in self.id_chars: return self.s305()
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s304(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)

    def s305(self):
        self.advance()
        if self._match_delimiter(self.id_delim): return self.s306()
        if self.current in self.id_chars:  return Token(Token.InvalidLexemeExceeds, self.get_lexeme(), self.start_line, self.start_col)
        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s306(self):
        return Token("id", self.get_lexeme(), self.start_line, self.start_col)