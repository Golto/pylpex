
from typing import List, Optional
from src.lexer import TokenType, Token
from .ASTNodes import *

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
class Parser:

    BINARY_PRECEDENCE = {
        TokenType.OR: 1,
        TokenType.AND: 2,
        TokenType.EQ: 3, TokenType.NEQ: 3,
        TokenType.LT: 4, TokenType.GT: 4, TokenType.LTE: 4, TokenType.GTE: 4,
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
    }

    UNARY_TOKEN_TO_ENUM = {
        TokenType.PLUS: UnaryOperatorType.POSITIVE,
        TokenType.MINUS: UnaryOperatorType.NEGATIVE,
        TokenType.NOT: UnaryOperatorType.NOT,
    }

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[0] if tokens else None

    # -----------------------------------------------------
    # Common methods

    def advance(self):
        """Avance au token suivant"""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None
    

    def peek(self, offset: int = 1):
        """Regarde le token à une position future"""
        peek_position = self.position + offset
        return self.tokens[peek_position] if peek_position < len(self.tokens) else None
    

    def expect(self, token_type):
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
    
    # -----------------------------------------------------
    # Parsing methods

    def parse(self) -> ProgramNode:
        """Point d'entrée: parse tout le programme"""
        statements = []
        
        self.skip_whitespace_and_comments()
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            self.skip_whitespace_and_comments()
            
            if self.current_token and self.current_token.type != TokenType.EOF:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            
            self.skip_whitespace_and_comments()
        
        return ProgramNode(statements)
    

    def parse_statement(self) -> Optional[ASTNode]:
        """Parse un statement (instruction)"""
        self.skip_whitespace_and_comments()
        
        if not self.current_token or self.current_token.type == TokenType.EOF:
            return None
        
        # TODO keywords
        
        # Expression statement
        expr = self.parse_expression()
        self.skip_whitespace_and_comments()
        
        # Optionnel: Semicolon
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        
        return expr
    

    def parse_expression(self, min_prec: int = 0) -> ASTNode:
        """Pratt / precedence climbing expression parser that also handles ternary"""
        self.skip_whitespace_and_comments()
        left = self.parse_unary_or_primary()

        # TODO while loop, binops, ternary

        return left
    

    def parse_unary_or_primary(self) -> ASTNode:
        """Gère opérateurs unaires et primaires/postfix"""
        self.skip_whitespace_and_comments()
        token = self.current_token
        if token and token.type in self.UNARY_TOKEN_TO_ENUM:
            op = self.UNARY_TOKEN_TO_ENUM[token.type]
            self.advance()
            operand = self.parse_unary_or_primary()
            return UnaryOpNode(operator=op, operand=operand)
        # else primary with possible postfix (call, attr, index)
        node = self.parse_primary()
        return self.parse_postfix(node)
    

    def parse_postfix(self, node: ASTNode) -> ASTNode:
        """Gère appels, attributs et indexations en chaîne: a.b(c)[i]"""
        while self.current_token:
            token = self.current_token

            # # call: IDENTIFIER '(' ... ')'
            # if token.type == TokenType.LPAREN:
            #     self.advance()  # consume '('
            #     args = []
            #     self.skip_whitespace_and_comments()
            #     if self.current_token and self.current_token.type != TokenType.RPAREN:
            #         while True:
            #             arg = self.parse_expression()
            #             args.append(arg)
            #             self.skip_whitespace_and_comments()
            #             if self.current_token and self.current_token.type == TokenType.COMMA:
            #                 self.advance()
            #                 self.skip_whitespace_and_comments()
            #                 continue
            #             break
            #     self.expect(TokenType.RPAREN)
            #     # function may be IdentifierNode or something else; for AST we kept CallNode.function as str earlier,
            #     # but better to store the function expression; here we handle simple identifier names
            #     if isinstance(node, IdentifierNode):
            #         node = CallNode(function=node.name, arguments=args)
            #     else:
            #         # if more complex (attribute call), wrap attribute/object representation as string?
            #         # Simpler: convert to CallNode with function repr
            #         node = CallNode(function=repr(node), arguments=args)
            #     continue

            # attribute .name
            if token.type == TokenType.DOT:
                self.advance()
                if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
                    raise ParseError("Attribut attendu après '.'", self.current_token)
                attr_name = self.current_token.value
                self.advance()
                node = AttributeNode(object=node, attribute=attr_name)
                continue

            # index [expr]
            if token.type == TokenType.LBRACKET:
                self.advance()
                index_expr = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                node = IndexNode(collection=node, index=index_expr)
                continue

            break

        return node

    
    def parse_primary(self):
        """Parse les expressions primaires: nombres, strings, identifiants, listes, etc."""
        self.skip_whitespace_and_comments()
        
        if not self.current_token:
            raise ParseError("Expression attendue, obtenu EOF")
        
        # None
        if self.current_token.type == TokenType.NONE:
            self.advance()
            return NoneNode()
        
        # Numbers
        if self.current_token.type == TokenType.INTEGER:
            value = int(self.current_token.value)
            self.advance()
            return NumberNode(value, NumberType.INTEGER)
        
        if self.current_token.type == TokenType.FLOAT:
            value = float(self.current_token.value)
            self.advance()
            return NumberNode(value, NumberType.FLOAT)
        
        # Strings
        if self.current_token.type == TokenType.STRING:
            value = self.current_token.value
            self.advance()
            return StringNode(value)
        
        # Booleans
        if self.current_token.type == TokenType.BOOLEAN:
            value = self.current_token.value == 'true'
            self.advance()
            return BooleanNode(value)
        
        # Identifiers
        if self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.advance()
            return IdentifierNode(name)
        
        # Parentheses (group)
        if self.current_token.type == TokenType.LPAREN:
            self.advance()
            self.skip_whitespace_and_comments()
            expr = self.parse_expression()
            self.skip_whitespace_and_comments()
            self.expect(TokenType.RPAREN)
            return expr
        
        # Lists
        if self.current_token.type == TokenType.LBRACKET:
            return self.parse_list()

        # Dictionnaries
        if self.current_token.type == TokenType.LBRACE:
            return self.parse_dictionary()
        
        raise ParseError(f"Expression inattendue: {self.current_token.type.value}", self.current_token)
    
    
    def parse_list(self) -> ListNode:
        self.expect(TokenType.LBRACKET)
        elements = []
        self.skip_whitespace_and_comments()
        if self.current_token and self.current_token.type != TokenType.RBRACKET:
            while True:
                elem = self.parse_expression()
                elements.append(elem)
                self.skip_whitespace_and_comments()
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                    self.skip_whitespace_and_comments()
                    continue
                break
        self.expect(TokenType.RBRACKET)
        return ListNode(elements=elements)
    

    def parse_dictionary(self) -> DictionaryNode:
        self.expect(TokenType.LBRACE)
        pairs = []
        self.skip_whitespace_and_comments()
        if self.current_token and self.current_token.type != TokenType.RBRACE:
            while True:
                key = self.parse_expression()
                self.skip_whitespace_and_comments()
                self.expect(TokenType.COLON)
                self.skip_whitespace_and_comments()
                value = self.parse_expression()
                pairs.append((key, value))
                self.skip_whitespace_and_comments()
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                    self.skip_whitespace_and_comments()
                    continue
                break
        self.expect(TokenType.RBRACE)
        return DictionaryNode(pairs=pairs)

    # -----------------------------------------------------
    # Helper methods

    def __repr__(self):
        return f"<Parser position={self.position} current_token={self.current_token}>"