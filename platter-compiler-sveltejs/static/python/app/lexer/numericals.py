from app.lexer.protocol import LexerProtocol
from app.lexer.token import Token


class LexerNumericals(LexerProtocol):
    def s307(self):  # -
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s308()
        if self.current == ".": return self.s311()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s308(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s309(self):  # Digit 1
        self.advance()
        if self.current in self.numeric: return self.s312()
        if self.current == ".": return self.s311()
        if self._match_delimiter(self.num_delim): return self.s310()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s310(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s311(self):  # . (Decimal point)
        self.advance()
        if self.current in self.numeric: return self.s340()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s312(self):  # Digit 2
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s313()
        if self.current in self.numeric: return self.s314()
        if self.current == ".": return self.s311()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s313(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s314(self):  # Digit 3
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s315()
        if self.current in self.numeric: return self.s316()
        if self.current == ".": return self.s311()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s315(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s316(self):  # Digit 4
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s317()
        if self.current in self.numeric: return self.s318()
        if self.current == ".": return self.s311()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s317(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s318(self):  # Digit 5
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s319()
        if self.current in self.numeric: return self.s320()
        if self.current == ".": return self.s311()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s319(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s320(self):  # Digit 6
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s321()
        if self.current in self.numeric: return self.s322()
        if self.current == ".": return self.s311()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s321(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s322(self):  # Digit 7
        self.advance()
        if self._match_delimiter(self.num_delim): return Token("piece_lit", self.get_lexeme(), self.start_line,
                                                               self.start_col)
        if self.current in self.numeric: return self.s324()
        if self.current == ".": return self.s311()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s323(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s324(self):  # Digit 8
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s325()
        if self.current in self.numeric: return self.s326()
        if self.current == ".": return self.s311()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s325(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s326(self):  # Digit 9
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s327()
        if self.current in self.numeric: return self.s328()
        if self.current == ".": return self.s311()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s327(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s328(self):  # Digit 10
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s329()
        if self.current in self.numeric: return self.s330()
        if self.current == ".": return self.s311()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s329(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s330(self):  # Digit 11
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s331()
        if self.current in self.numeric: return self.s332()
        if self.current == ".": return self.s311()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s331(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s332(self):  # Digit 12
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s333()
        if self.current in self.numeric: return self.s334()
        if self.current == ".": return self.s311()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s333(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s334(self):  # Digit 13
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s335()
        if self.current in self.numeric: return self.s336()
        if self.current == ".": return self.s311()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s335(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s336(self):  # Digit 14
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s337()
        if self.current in self.numeric: return self.s338()
        if self.current == ".": return self.s311()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s337(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s338(self):  # Digit 15 (Max whole digits)
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s339()
        if self.current == ".": return self.s311()
        if self.current in self.numeric: return [Token(Token.InvalidLexemeExceeds, self.get_lexeme(), self.start_line, self.start_col)]
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s339(self):
        return Token("piece_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s340(self):  # Decimal Digit 1
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s341()
        if self.current in self.numeric: return self.s342()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s341(self):
        return Token("sip_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s342(self):  # Decimal Digit 2
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s343()
        if self.current in self.numeric: return self.s344()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s343(self):
        return Token("sip_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s344(self):  # Decimal Digit 3
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s345()
        if self.current in self.numeric: return self.s346()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s345(self):
        return Token("sip_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s346(self):  # Decimal Digit 4
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s347()
        if self.current in self.numeric: return self.s348()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s347(self):
        return Token("sip_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s348(self):  # Decimal Digit 5
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s349()
        if self.current in self.numeric: return self.s350()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s349(self):
        return Token("sip_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s350(self):  # Decimal Digit 6
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s351()
        if self.current in self.numeric: return self.s352()
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s351(self):
        return Token("sip_lit", self.get_lexeme(), self.start_line,
                     self.start_col)

    def s352(self):  # Decimal Digit 7 (Max decimal digits)
        self.advance()
        if self._match_delimiter(self.num_delim): return self.s353()
        if self.current in self.numeric: return [Token(Token.InvalidLexemeExceeds, self.get_lexeme(), self.start_line, self.start_col)]
        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s353(self):
        return Token("sip_lit", self.get_lexeme(), self.start_line,
                     self.start_col)