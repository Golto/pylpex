# base.py
from src.lexer import TokenType, Token
from .ASTNodes import *
from typing import List, Optional

class ParseError(Exception):
    """Erreur de syntaxe détectée pendant l'analyse syntaxique"""
    def __init__(self, message: str, token=None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f"Erreur de syntaxe à la ligne {token.line}, colonne {token.column}: {message}")
        else:
            super().__init__(f"Erreur de syntaxe: {message}")

# TODO faire un mode strict pour les types
# self.strict = False -> typage facultatif et ne cause pas d'erreur
# self.strict = True -> typage obligatoire et cause une erreur si non respecté

# TODO implémenter NOT_IN "not in", détecter tokens: NOT, IN qui se suivent

# FIXME confusion entre [if/else] ternary et [if/else] block
# some_value = 45 if x > 5 else 67
# VS
# some_value = 45
# if x > 5 { ... } else 67

class BaseParser:

    BINARY_PRECEDENCE = {
        TokenType.OR: 1,
        TokenType.AND: 2,
        TokenType.EQ: 3, TokenType.NEQ: 3,
        TokenType.LT: 4, TokenType.GT: 4, TokenType.LTE: 4, TokenType.GTE: 4, TokenType.IN: 4,
        TokenType.PLUS: 5, TokenType.MINUS: 5,
        TokenType.MUL: 6, TokenType.DIV: 6, TokenType.MOD: 6,
        TokenType.POWER: 8,  # power is right-associative, handled specially
    }

    ASSIGNMENT_MAP = {
        TokenType.ASSIGN: AssignmentOperatorType.ASSIGN,
        TokenType.PLUS_ASSIGN: AssignmentOperatorType.PLUS,
        TokenType.MINUS_ASSIGN: AssignmentOperatorType.MINUS,
        TokenType.MUL_ASSIGN: AssignmentOperatorType.MUL,
        TokenType.DIV_ASSIGN: AssignmentOperatorType.DIV,
        TokenType.MOD_ASSIGN: AssignmentOperatorType.MOD,
        TokenType.POWER_ASSIGN: AssignmentOperatorType.POWER,
    }

    BINARY_TOKEN_TO_ENUM = {
        TokenType.PLUS: BinaryOperatorType.PLUS,
        TokenType.MINUS: BinaryOperatorType.MINUS,
        TokenType.MUL: BinaryOperatorType.MUL,
        TokenType.DIV: BinaryOperatorType.DIV,
        TokenType.MOD: BinaryOperatorType.MOD,
        TokenType.POWER: BinaryOperatorType.POWER,
        TokenType.AND: BinaryOperatorType.AND,
        TokenType.OR: BinaryOperatorType.OR,
        TokenType.EQ: BinaryOperatorType.EQ,
        TokenType.NEQ: BinaryOperatorType.NEQ,
        TokenType.LT: BinaryOperatorType.LT,
        TokenType.GT: BinaryOperatorType.GT,
        TokenType.LTE: BinaryOperatorType.LTE,
        TokenType.GTE: BinaryOperatorType.GTE,
        TokenType.IN: BinaryOperatorType.IN,
        TokenType.NOT: BinaryOperatorType.NOT_IN, # TODO: vérifier si c'est correct
    }

    UNARY_TOKEN_TO_ENUM = {
        TokenType.PLUS: UnaryOperatorType.POSITIVE,
        TokenType.MINUS: UnaryOperatorType.NEGATIVE,
        TokenType.NOT: UnaryOperatorType.NOT,
    }

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0] if tokens else None
        self.loop_depth = 0 # loop context (for break/continue)


    def advance(self):
        """Avance au token suivant"""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None


    def peek(self, offset: int = 1) -> Optional[Token]:
        """Regarde le token à une position future"""
        peek_position = self.position + offset
        return self.tokens[peek_position] if peek_position < len(self.tokens) else None
    

    def expect(self, token_type) -> Token:
        """Vérifie que le token courant est du type attendu"""
        if not self.current_token or self.current_token.type != token_type:
            raise ParseError(
                f"Attendu {token_type.value}, obtenu {self.current_token.type.value if self.current_token else 'EOF'}",
                self.current_token
            )
        token = self.current_token
        self.advance()
        return token
    

    # -----------------------------------------------------
    # Skipping methods

    def skip_newlines(self):
        """Ignore les retours à la ligne"""
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()
    

    def skip_comments(self):
        """Ignore les commentaires"""
        while self.current_token and self.current_token.type == TokenType.COMMENT:
            self.advance()
    

    def skip_whitespace_and_comments(self):
        """Ignore les espaces et commentaires"""
        while self.current_token and self.current_token.type in (TokenType.NEWLINE, TokenType.COMMENT):
            self.advance()
