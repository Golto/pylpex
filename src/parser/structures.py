from src.lexer import TokenType
from .ASTNodes import *
from .base import BaseParser, ParseError

class StructureParser(BaseParser):

    def parse_list(self) -> ListNode:
        token = self.expect(TokenType.LBRACKET)
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
        return ListNode.from_token(token, elements=elements)
    

    def parse_dictionary(self) -> DictionaryNode:
        token = self.expect(TokenType.LBRACE)
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
        return DictionaryNode.from_token(token, pairs=pairs)

    
    def parse_argument_list(self) -> List[ArgumentNode]:
        """Parse les arguments d'appel de fonction (f(a, b, x=4))"""
        args = []
        self.expect(TokenType.LPAREN)
        self.skip_whitespace_and_comments()

        if self.current_token and self.current_token.type != TokenType.RPAREN:
            while True:
                token = self.current_token
                expr = self.parse_expression()
                # If a '=' follows, it is a named argument
                if isinstance(expr, IdentifierNode) and self.current_token and self.current_token.type == TokenType.ASSIGN:
                    self.advance()  # consomme '='
                    value = self.parse_expression()
                    args.append(ArgumentNode.from_token(token, name=expr.name, value=value))
                else:
                    args.append(ArgumentNode.from_token(token, name=None, value=expr))

                self.skip_whitespace_and_comments()
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                    self.skip_whitespace_and_comments()
                    continue
                break

        self.expect(TokenType.RPAREN)
        return args
    

    def parse_block(self) -> List[ASTNode]:
        """Bloque délimité par { ... }"""
        self.expect(TokenType.LBRACE)
        stmts = []
        self.skip_whitespace_and_comments()
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
            self.skip_whitespace_and_comments()
        self.expect(TokenType.RBRACE)
        return stmts