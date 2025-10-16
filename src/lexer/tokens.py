from typing import Tuple
from enum import Enum
from dataclasses import dataclass


class TokenType(Enum):
    # Data types
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    COMPLEX = "COMPLEX"
    VECTOR = "VECTOR"
    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    # Keywords
    FUNCTION = "FUNCTION"
    RETURN = "RETURN"
    IF = "IF"
    ELSE = "ELSE"
    # Identifiers
    IDENTIFIER = "IDENTIFIER"
    

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

