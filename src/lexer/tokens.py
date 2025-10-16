from typing import Tuple
from enum import Enum
from dataclasses import dataclass

# TODO add keywords: in, break, continue
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
    # Keywords
    FUNCTION = "FUNCTION"
    RETURN = "RETURN"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    FOR = "FOR"
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

    def __post_init__(self):
        if not isinstance(self.type, TokenType):
            raise ValueError("Token type must be a TokenType enum member")
        
    def get_position(self) -> Tuple[int, int]:
        return (self.line, self.column)

