
from app.lexer.numericals import LexerNumericals
from app.lexer.token import Token
from app.lexer.base import LexerBase
from app.lexer.keywords import LexerKeywords
from app.lexer.operators import LexerOperators
from app.lexer.identifiers import LexerIdentifier
from app.lexer.char_com import LexerCharCom
from pprint import pprint
import os
import subprocess


class Lexer(LexerBase, LexerKeywords, LexerOperators, LexerIdentifier, LexerCharCom, LexerNumericals):
    def s0(self):
        if self.current is None: return None

        self.save_start()

        # print("current", self.current)
        if self.current == 'a' and (tok := self.s1()): return tok
        if self.current == 'b' and (tok := self.s14()): return tok
        if self.current == 'c' and (tok := self.s19()): return tok
        if self.current == 'd' and (tok := self.s41()): return tok
        if self.current == 'f' and (tok := self.s46()): return tok
        if self.current == 'i' and (tok := self.s55()): return tok
        if self.current == 'm' and (tok := self.s63()): return tok
        if self.current == 'n' and (tok := self.s75()): return tok
        if self.current == 'o' and (tok := self.s83()): return tok
        if self.current == 'p' and (tok := self.s92()): return tok
        if self.current == 'r' and (tok := self.s112()): return tok
        if self.current == 's' and (tok := self.s134()): return tok
        if self.current == 't' and (tok := self.s167()): return tok
        if self.current == 'u' and (tok := self.s193()): return tok

        if self.current == "+" and (tok := self.s201()): return tok
        if self.current == "-" and (tok := self.s205()): return tok
        if self.current == "*" and (tok := self.s209()): return tok
        if self.current == "/" and (tok := self.s213()): return tok
        if self.current == "%" and (tok := self.s217()): return tok
        if self.current == ">" and (tok := self.s221()): return tok
        if self.current == "<" and (tok := self.s225()): return tok
        if self.current == "=" and (tok := self.s229()): return tok
        if self.current == "!" and (tok := self.s233()): return tok

        if self.current == " " and (tok := self.s236()): return tok
        if self.current == "\t" and (tok := self.s237()): return tok
        if self.current == "\n" and (tok := self.s238()): return tok
        if self.current == "," and (tok := self.s239()): return tok
        if self.current == ":" and (tok := self.s241()): return tok
        if self.current == ";" and (tok := self.s243()): return tok
        if self.current == "(" and (tok := self.s245()): return tok
        if self.current == ")" and (tok := self.s247()): return tok
        if self.current == "[" and (tok := self.s249()): return tok
        if self.current == "]" and (tok := self.s251()): return tok
        if self.current == "{" and (tok := self.s253()): return tok
        if self.current == "}" and (tok := self.s255()): return tok

        if self.current in (self.alpha + self.underscore) and (tok := self.s257()): return tok
        if self.current == "0" and (tok := self.s307()): return tok
        if self.current in self.digit and (tok := self.s309()): return tok
        if self.current == '"' and (tok := self.s354()): return tok
        if self.current == '#' and (tok := self.s357()): return tok

        tok = Token(Token.InvalidCharacter, self.current, self.start_line, self.start_col)
        self.advance()
        return tok

    def tokenize(self):
        """Returns a list of all tokens from the input text."""
        tokens = []
        counter = 0
        while self.current is not None:
            tok = self.s0()
            if not tok: break
            if isinstance(tok, list): tokens.extend(tok)
            else: tokens.append(tok)
            # print("Counter:", counter)
            # print("Token:", tok, "\n\n\n")
            counter += 1
        return tokens

if __name__ == "__main__":



    filepath = "./tests/sample_program.txt"

    include_whitespace = False # choice == 'y'

    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    tokens = [
        t for t in tokens
        if t.type not in ("comment", "space", "newline", "tab") or include_whitespace
    ]

    def set_clipboard(text: str):
        subprocess.run("clip", universal_newlines=True, input=text)
    print("\n\nTOKENS:")
    pprint(tokens)
    set_clipboard((" ".join(t.type for t in tokens if not "comment" in t.type )))   