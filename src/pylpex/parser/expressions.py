from pylpex.lexer import TokenType
from .ASTNodes import *
from .base import BaseParser, SyntaxicalError


class ExpressionParser(BaseParser):

    def parse_expression(self, min_prec: int = 0) -> ASTNode:
        """Pratt / precedence climbing expression parser that also handles ternary"""
        self.skip_comments()
        left = self.parse_unary_or_primary()

        while True:
            self.skip_comments()
            token = self.current_token
            if not token:
                break

            # <true_expr> if <cond> else <false_expr>
            if token.type == TokenType.IF:
                self.advance()  # consume 'if'
                cond = self.parse_expression()
                self.skip_whitespace_and_comments()
                if not self.current_token or self.current_token.type != TokenType.ELSE:
                    raise SyntaxicalError("Ternary 'if' sans 'else'", token)
                self.advance()  # consume 'else'
                false_expr = self.parse_expression()
                left = TernaryNode.from_token(token, condition=cond, true_expr=left, false_expr=false_expr)
                continue

            # binary operator
            if token.type in self.BINARY_PRECEDENCE:
                prec = self.BINARY_PRECEDENCE[token.type]
                # power operator is right associative
                right_assoc = (token.type == TokenType.POWER)
                if prec < min_prec:
                    break
                self.advance()  # consume operator
                # For right-assoc, use prec, else use prec+1
                next_min = prec + (0 if right_assoc else 1)
                right = self.parse_expression(next_min)
                binop = self.BINARY_TOKEN_TO_ENUM.get(token.type)
                if not binop:
                    raise SyntaxicalError(f"Opérateur binaire non-supporté: {token.type}", token)
                left = BinaryOpNode.from_token(token, left=left, operator=binop, right=right)
                continue

            break

        return left
    

    def parse_unary_or_primary(self) -> ASTNode:
        """Gère opérateurs unaires et primaires/postfix"""
        self.skip_whitespace_and_comments()
        token = self.current_token
        if token and token.type in self.UNARY_TOKEN_TO_ENUM:
            op = self.UNARY_TOKEN_TO_ENUM[token.type]
            self.advance()
            operand = self.parse_unary_or_primary()
            return UnaryOpNode.from_token(token, operator=op, operand=operand)
        # else primary with possible postfix (call, attr, index)
        node = self.parse_primary()
        return self.parse_postfix(node)
    

    def parse_postfix(self, node: ASTNode) -> ASTNode:
        """Gère appels, attributs et indexations en chaîne: a.b(c)[i]"""
        while self.current_token:
            token = self.current_token

            # call: IDENTIFIER '(' ... ')'
            if token.type == TokenType.LPAREN:
                args = self.parse_argument_list()
                if isinstance(node, IdentifierNode):
                    node = CallNode.from_token(token, function=node.name, arguments=args)
                else:
                    node = CallNode.from_token(token, function=node, arguments=args)
                continue

            # attribute .name
            if token.type == TokenType.DOT:
                self.advance()
                if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
                    raise SyntaxicalError("Attribut attendu après '.'", self.current_token)
                attr_name = self.current_token.value
                self.advance()
                node = AttributeNode.from_token(token, object=node, attribute=attr_name)
                continue

            # index [expr]
            if token.type == TokenType.LBRACKET:
                self.advance()
                index_expr = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                node = IndexNode.from_token(token, collection=node, index=index_expr)
                continue

            break

        return node

    
    def parse_primary(self) -> ASTNode:
        """Parse les expressions primaires: nombres, strings, identifiants, listes, etc."""
        self.skip_whitespace_and_comments()
        
        if not self.current_token:
            raise SyntaxicalError("Expression attendue, obtenu EOF")
        
        token = self.current_token
        
        # None
        if token.type == TokenType.NONE:
            self.advance()
            return NoneNode.from_token(token)
        
        # Numbers
        if token.type == TokenType.INTEGER:
            value = int(token.value)
            self.advance()
            return NumberNode.from_token(token, value=value, type=NumberType.INTEGER)
        
        if token.type == TokenType.FLOAT:
            value = float(token.value)
            self.advance()
            return NumberNode.from_token(token, value=value, type=NumberType.FLOAT)
        
        # Strings
        if token.type == TokenType.STRING:
            value = token.value
            self.advance()
            return StringNode.from_token(token, value=value)
        
        # Booleans
        if token.type == TokenType.BOOLEAN:
            value = token.value == 'true'
            self.advance()
            return BooleanNode.from_token(token, value=value)
        
        # Identifiers
        if token.type == TokenType.IDENTIFIER:
            name = token.value
            self.advance()
            return IdentifierNode.from_token(token, name=name)
        
        # Parentheses (group)
        if token.type == TokenType.LPAREN:
            self.advance()
            self.skip_whitespace_and_comments()
            expr = self.parse_expression()
            self.skip_whitespace_and_comments()
            self.expect(TokenType.RPAREN)
            return expr
        
        # Lists
        if token.type == TokenType.LBRACKET:
            return self.parse_list()

        # Dictionnaries
        if token.type == TokenType.LBRACE:
            return self.parse_dictionary()
        
        raise SyntaxicalError(f"Expression inattendue: {token.type.value}", token)
    
