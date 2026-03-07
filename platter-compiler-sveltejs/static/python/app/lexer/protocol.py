from typing import Protocol, Optional, Tuple
from app.lexer.token import Token


class LexerProtocol(Protocol):

    # Position tracking
    text: str
    pos: int
    line: int
    col: int
    start_pos: int
    start_col: int
    start_line: int
    current: Optional[str]
    
    # Character sets based on formal specification
    underscore: list[str]
    zero: list[str]
    digit: list[str]
    numeric: list[str]
    lowercase: list[str]
    uppercase: list[str]
    alpha: list[str]
    alphanumeric: list[str]
    id_chars: list[str]
    flag: list[str]
    arithm_op: list[str]
    logic_op: list[str]
    assign_op: list[str]
    rel_op: list[str]
    period: list[str]
    newline: list[str]
    tab: list[str]
    space: list[str]
    whitespace: list[str]
    ascii: list[str]
    ascii_1: list[str]
    ascii_2: list[str]
    ascii_3: list[str]
    
    # Keywords
    KEYWORDS: list[str]
    
    # Delimiters based on formal specification
    colon_dlm: list[str]
    curly_dlm: list[str]
    dtype_dlm: list[str]
    equal_dlm: list[str]
    flag_dlm: list[str]
    id_delim: list[str]
    num_delim: list[str]
    op1_dlm: list[str]
    op2_dlm: list[str]
    paren_dlm: list[str]
    term_dlm: list[str]
    dlm_1: list[str]
    dlm_2: list[str]
    dlm_3: list[str]
    dlm_4: list[str]
    dlm_5: list[str]
    dlm_6: list[str]
    dlm_7: list[str]
    dlm_8: list[str]
    dlm_9: list[str]
    
    # Methods
    def advance(self) -> None: ...
    def save(self) -> Tuple[int, int, int, Optional[str]]: ...
    def restore(self) -> None: ...
    def save_start(self) -> None: ...
    def get_lexeme(self) -> str: ...
    def _match_delimiter(self, delimiters: list[str]) -> bool: ...

    def s309(self) -> Token: ...
    def s307(self) -> Token: ...