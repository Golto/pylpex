from typing import Tuple, Optional
from enum import Enum
from dataclasses import dataclass

class TokenType(Enum):
    # Data types
    NONE = "NONE"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    LIST = "LIST"
    DICTIONARY = "DICTIONARY"
    # Identifiers
    IDENTIFIER = "IDENTIFIER"
    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    POWER = "POWER"
    MOD = "MOD"
    # Logical operators
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    # Comparison
    EQ = "EQ"
    NEQ = "NEQ"
    LT = "LT"
    GT = "GT"
    LTE = "LTE"
    GTE = "GTE"
    # Assignment
    ASSIGN = "ASSIGN"
    PLUS_ASSIGN = "PLUS_ASSIGN"
    MINUS_ASSIGN = "MINUS_ASSIGN"
    MUL_ASSIGN = "MUL_ASSIGN"
    DIV_ASSIGN = "DIV_ASSIGN"
    MOD_ASSIGN = "MOD_ASSIGN"
    POWER_ASSIGN = "POWER_ASSIGN"
    # Delimiters
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    COLON = "COLON"
    DOT = "DOT"
    ARROW = "ARROW"
    # Keywords
    FUNCTION = "FUNCTION"
    RETURN = "RETURN"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    FOR = "FOR"
    IN = "IN"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"
    # Special
    EOF = "EOF"
    COMMENT = "COMMENT"
    NEWLINE = "NEWLINE"

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.value}>"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

    _actual_value: Optional[str] = None

    def __post_init__(self):
        if not isinstance(self.type, TokenType):
            raise ValueError("Token type must be a TokenType enum member")
        
    def get_position(self) -> Tuple[int, int]:
        return (self.line, self.column)
    
    def get_actual_value(self) -> str:
        if self._actual_value is not None:
            return self._actual_value
        return self.value

