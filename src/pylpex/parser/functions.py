from pylpex.lexer import TokenType
from .ASTNodes import *
from .base import BaseParser, SyntaxicalError
from pylpex.typesystem import TypeInfo, BaseType

class FunctionParser(BaseParser):

    def parse_function_def(self) -> FunctionDefNode:
        """Parse une définition de fonction"""
        func_token = self.expect(TokenType.FUNCTION)
        if not (self.current_token and self.current_token.type == TokenType.IDENTIFIER):
            raise SyntaxicalError("Nom de fonction attendu", self.current_token)
        
        name = self.current_token.value
        self.advance()
        return_type_annotation = None

        params = self.parse_parameter_list()
        self.skip_whitespace_and_comments()

        if self.current_token and self.current_token.type == TokenType.ARROW:
            self.advance()
            self.skip_whitespace_and_comments()
            return_type_annotation = self.parse_type()
        
        body = self.parse_block()
        return FunctionDefNode.from_token(func_token, 
            name=name, 
            parameters=params, 
            body=body,
            return_type=return_type_annotation,
            type_annotation=TypeInfo.callable(
                arg_types=[p.type_annotation or TypeInfo(BaseType.ANY) for p in params],
                return_type=return_type_annotation or TypeInfo(BaseType.ANY)
            )
        )


    def parse_parameter(self) -> ParameterNode:
        """Parse un seul paramètre, avec valeur par défaut et typage optionnel"""
        self.skip_whitespace_and_comments()
        if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
            raise SyntaxicalError("Nom de paramètre attendu", self.current_token)

        name = self.current_token.value
        self.advance()
        type_annotation = None
        default_value = None

        self.skip_whitespace_and_comments()

        # Manage type annotations
        if self.current_token and self.current_token.type == TokenType.COLON:
            self.advance()
            self.skip_whitespace_and_comments()
            type_annotation = self.parse_type()

        # Valeur par défaut : "= expression"
        if self.current_token and self.current_token.type == TokenType.ASSIGN:
            self.advance()
            default_value = self.parse_expression()

        return ParameterNode(name=name, default_value=default_value, type_annotation=type_annotation)


    def parse_parameter_list(self) -> List[ParameterNode]:
        """Parse la liste des paramètres d'une fonction"""
        params = []
        self.expect(TokenType.LPAREN)
        self.skip_whitespace_and_comments()

        if self.current_token and self.current_token.type != TokenType.RPAREN:
            while True:
                param = self.parse_parameter()
                params.append(param)
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