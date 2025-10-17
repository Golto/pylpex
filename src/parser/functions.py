from src.lexer import TokenType
from .ASTNodes import *
from .base import BaseParser, ParseError

class FunctionParser(BaseParser):

    def parse_function_def(self) -> FunctionDefNode:
        func_token = self.expect(TokenType.FUNCTION)
        if not (self.current_token and self.current_token.type == TokenType.IDENTIFIER):
            raise ParseError("Nom de fonction attendu", self.current_token)
        name = self.current_token.value
        self.advance()
        params = self.parse_parameter_list()
        self.skip_whitespace_and_comments()
        body = self.parse_block()
        return FunctionDefNode.from_token(func_token, name=name, parameters=params, body=body)


    def parse_parameter_list(self) -> List[ParameterNode]:
        """Parse la liste des paramètres d'une fonction"""
        params = []
        self.expect(TokenType.LPAREN)
        self.skip_whitespace_and_comments()

        if self.current_token and self.current_token.type != TokenType.RPAREN:
            while True:
                if self.current_token.type != TokenType.IDENTIFIER:
                    raise ParseError("Nom de paramètre attendu", self.current_token)
                name_token = self.current_token
                self.advance()
                default_value = None
                # valeur par défaut : " = expression"
                if self.current_token and self.current_token.type == TokenType.ASSIGN:
                    self.advance()
                    default_value = self.parse_expression()
                params.append(ParameterNode.from_token(name_token, name=name_token.value, default_value=default_value))

                self.skip_whitespace_and_comments()
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                    self.skip_whitespace_and_comments()
                    continue
                break

        self.expect(TokenType.RPAREN)
        return params
    

    def parse_return(self) -> ReturnNode:
        token = self.expect(TokenType.RETURN)
        # optional expression
        if self.current_token and self.current_token.type not in (TokenType.SEMICOLON, TokenType.NEWLINE, TokenType.EOF, TokenType.RBRACE):
            val = self.parse_expression()
        else:
            val = None
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return ReturnNode.from_token(token, value=val)