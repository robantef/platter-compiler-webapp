from app.lexer.token import Token


class LexerBase:

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.start_pos = 0
        self.start_col = 1
        self.start_line = 1
        self.current = self.text[self.pos] if self.text else None

        self.underscore = ['_']
        self.zero = ['0']
        self.digit = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.numeric = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.lowercase = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 
                          'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        self.uppercase = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                          'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        self.alpha = self.lowercase + self.uppercase
        self.alphanumeric = self.alpha + self.numeric
        self.id_chars = self.alphanumeric + self.underscore
        self.flag = ['up', 'down']
        self.arithm_op = ['+', '-', '*', '/', '%']
        self.logic_op = ['and', 'or', 'not']
        self.assign_op = ['=', '+=', '-=', '/=', '*=', '%=']
        self.rel_op = ['!=', '==', '<', '>', '<=', '>=']
        self.period = ['.']
        self.newline = ['\n']
        self.tab = ['\t']
        self.space = [' ']
        self.whitespace = ['\n', '\t', ' ']
        self.ascii = self.alphanumeric + self.arithm_op + [' ', '!', '"', '#', '$', '&', "'", '(', ')', ',', '.', ':', ';', '<', '=', '>', 
                                                            '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']
        self.ascii_1 = [c for c in self.ascii if c not in ['\\', '"']]
        self.ascii_2 = self.ascii + ['\t']
        self.ascii_3 = [c for c in self.ascii if c != '#'] + ['\n', '\t']

        self.colon_dlm = self.whitespace + [':']
        self.curly_dlm = self.whitespace + ['{']
        self.dtype_dlm = self.whitespace + ['[']
        self.equal_dlm = self.whitespace + self.alphanumeric + ['(', '[', '-', '_', '"']
        self.flag_dlm = self.whitespace + ['(', ')', '[', ']', ';', '=', '!', '"', ","]
        self.id_delim = self.whitespace + ['(', ')', '[', ']', ';', '=', '+', '-', '*', '/', '%', '!', '<', '>', ',', ':', '#']
        self.num_delim = self.whitespace + ['(', ')', ']', ';', '=', '+', '-', '*', '/', '%', '!', '<', '>', ',', ':']
        self.op1_dlm = self.whitespace + self.alphanumeric + ['(', '-', '_', '"']
        self.op2_dlm = self.whitespace + self.alpha + ['(', '_', '"']
        self.paren_dlm = self.whitespace + ['(']
        self.term_dlm = self.whitespace + [';']

        self.dlm_1 = self.whitespace + self.alphanumeric + ['(', '[', '-', '_', '"', '#']
        self.dlm_2 = self.whitespace + self.alpha + ['_', '}', '#']
        self.dlm_3 = self.whitespace + self.alphanumeric + ['(', ']', '-', '}', '_', '"', '#']
        self.dlm_4 = self.whitespace + self.alphanumeric + ['(', ')', '[', '-', '_', '"', '#']
        self.dlm_5 = self.whitespace + [')', ';', '+', '-', '*', '/', '%', '!', '<', '>', ',', '{', '#', '=']
        self.dlm_6 = self.whitespace + self.alphanumeric + ['[', ']', '-', '_', '"', '#']
        self.dlm_7 = self.whitespace + [')', '[', ']', ';', '=', '+', '-', '*', '/', '%', '!', '<', '>', ',', ':', '#']
        self.dlm_8 = self.whitespace + self.alpha + ['}', '#', '_']
        self.dlm_9 = self.whitespace + self.alpha + ['_', '#', '}', None]

    def advance(self):
        """Moves to the next character, updating line and column."""
        if self.current == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.pos += 1
        self.current = self.text[self.pos] if self.pos < len(self.text) else None

    def restore(self):
        """Restores a saved state."""
        self.pos = self.start_pos
        self.line = self.start_line
        self.col = self.start_col
        self.current = self.text[self.pos] if self.pos < len(self.text) else None

    def save_start(self):
        """Saves the starting position for the current potential token."""
        self.start_pos = self.pos
        self.start_col = self.col
        self.start_line = self.line

    def get_lexeme(self):
        """Returns the lexeme value from the start position to the current position."""
        return self.text[self.start_pos:self.pos]

    def _match_delimiter(self, delimiters):
        """Checks if the current character is a valid delimiter for an accepting state."""
        return self.current in delimiters