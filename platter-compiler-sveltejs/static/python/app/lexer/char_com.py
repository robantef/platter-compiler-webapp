from app.lexer.token import Token
from app.lexer.protocol import LexerProtocol


class LexerCharCom(LexerProtocol):

    def s354(self):
        self.advance()
        if self.current is None: return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

        if self.current in self.ascii_1: return self.s354()
        if self.current == '\\': return self.s355()
        if self.current == '"': return self.s356()

        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s355(self):
        self.advance()
        if self.current is None: return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)
        if self.current in self.ascii: return self.s354()

        return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)

    def s356(self):
        self.advance()
        return Token("chars_lit", self.get_lexeme(), self.start_line, self.start_col)

    def s357(self):
        self.advance()
        if self.current == ' ': return self.s358()
        if self.current == '#': return self.s360()

        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s358(self):
        self.advance()
        if self.current in self.ascii_2: return self.s358()
        if self.current == '\n': return self.s359()
        if self.current is None: return self.s359()

        return [Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)]

    def s359(self):
        return Token("comment_single", self.get_lexeme(), self.start_line, self.start_col)

    def s360(self):
        self.advance()
        if self.current is None: return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)
        if self.current == '#': return self.s361()

        return self.s360()

    def s361(self):
        self.advance()
        if self.current is None: return Token(Token.InvalidLexeme, self.get_lexeme(), self.start_line, self.start_col)
        if self.current == '#': return self.s362()

        return self.s360()

    def s362(self):
        self.advance()
        return Token("comment_multi", self.get_lexeme(), self.start_line, self.start_col)
