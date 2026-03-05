import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from lexer.lexer import Lexer

# Test what the lexer returns for a string literal
code = 'chars of text = "hello";'
lexer = Lexer(code)
tokens = lexer.tokenize()

for token in tokens:
    if token.type == 'chars_lit':
        print(f"Token type: {token.type}")
        print(f"Token value: {repr(token.value)}")
        print(f"Token value type: {type(token.value)}")
