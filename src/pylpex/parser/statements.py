from pylpex.lexer import TokenType
from .ASTNodes import *
from .base import BaseParser, ParseError

class StatementParser(BaseParser):

    def parse_statement(self) -> Optional[ASTNode]:
        """Parse un statement (instruction)"""
        self.skip_whitespace_and_comments()
        
        if not self.current_token or self.current_token.type == TokenType.EOF:
            return None
        
        # Manage keywords: function, if, while, for, return
        if self.current_token.type == TokenType.FUNCTION:
            return self.parse_function_def()
        if self.current_token.type == TokenType.IF:
            return self.parse_if()
        if self.current_token.type == TokenType.WHILE:
            return self.parse_while()
        if self.current_token.type == TokenType.FOR:
            return self.parse_for()
        if self.current_token.type == TokenType.RETURN:
            return self.parse_return()
        if self.current_token.type == TokenType.BREAK:
            return self.parse_break()
        if self.current_token.type == TokenType.CONTINUE:
            return self.parse_continue()
        
        # Expression statement
        expr = self.parse_expression()
        self.skip_whitespace_and_comments()

        # Assignment management
        if self.current_token and self.current_token.type in self.ASSIGNMENT_MAP:
            op_token = self.current_token
            op_type = self.ASSIGNMENT_MAP[op_token.type]
            self.advance()  # consumes the operator
            value = self.parse_expression()

            # Check that the target is assignable
            if not isinstance(expr, (IdentifierNode, AttributeNode, IndexNode)):
                raise ParseError("La partie gauche d'une affectation doit être une variable, un attribut ou un index", op_token)

            node = AssignmentNode.from_token(
                token=op_token,
                target=expr,
                operator=op_type,
                value=value
            )

            # Optional: Semicolon (for affectations)
            if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                self.advance()
            return node
            
        
        # Optional: Semicolon (for expressions)
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        
        return expr


    def parse_if(self) -> IfNode: # TODO ajouter la possibilité de faire "else if"
        start_token = self.expect(TokenType.IF)
        self.skip_whitespace_and_comments()
        # condition is an expression
        cond = self.parse_expression()
        self.skip_whitespace_and_comments()
        then_block = None
        else_block = None
        # block or single statement
        if self.current_token and self.current_token.type == TokenType.LBRACE:
            then_block = self.parse_block()
        else:
            # single statement fallback
            stmt = self.parse_statement()
            then_block = [stmt] if stmt else []
        self.skip_whitespace_and_comments()
        if self.current_token and self.current_token.type == TokenType.ELSE:
            self.advance()
            self.skip_whitespace_and_comments()
            if self.current_token and self.current_token.type == TokenType.LBRACE:
                else_block = self.parse_block()
            else:
                stmt = self.parse_statement()
                else_block = [stmt] if stmt else []
        return IfNode.from_token(start_token, condition=cond, then_block=then_block, else_block=else_block)


    def parse_while(self) -> WhileNode:
        start_token = self.expect(TokenType.WHILE)
        cond = self.parse_expression()
        self.skip_whitespace_and_comments()

        self.loop_depth += 1
        if self.current_token and self.current_token.type == TokenType.LBRACE:
            body = self.parse_block()
        else:
            stmt = self.parse_statement()
            body = [stmt] if stmt else []
        self.loop_depth -= 1

        return WhileNode.from_token(start_token, condition=cond, body=body)
    

    def parse_for(self) -> ForNode:
        """Parse une boucle for (for x in iterable { ... })"""
        start_token = self.expect(TokenType.FOR)

        # variable
        if not (self.current_token and self.current_token.type == TokenType.IDENTIFIER):
            raise ParseError("Nom de variable attendu après 'for'", self.current_token)
        var_name = self.current_token.value
        self.advance()

        # 'in' keyword
        if not (self.current_token and self.current_token.type == TokenType.IN):
            raise ParseError("Mot-clé 'in' attendu dans la boucle for", self.current_token)
        self.advance()

        # iterable expression
        iterable_expr = self.parse_expression()

        self.skip_whitespace_and_comments()
        self.loop_depth += 1
        body = self.parse_block()
        self.loop_depth -= 1

        return ForNode.from_token(start_token, variable=var_name, iterable=iterable_expr, body=body)


    def parse_break(self) -> BreakNode:
        """Parse l'instruction 'break'"""
        start_token = self.expect(TokenType.BREAK)
        if self.loop_depth == 0:
            raise ParseError("'break' ne peut être utilisé qu'à l'intérieur d'une boucle", self.current_token)

        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return BreakNode.from_token(start_token)


    def parse_continue(self) -> ContinueNode:
        """Parse l'instruction 'continue'"""
        start_token = self.expect(TokenType.CONTINUE)
        if self.loop_depth == 0:
            raise ParseError("'continue' ne peut être utilisé qu'à l'intérieur d'une boucle", self.current_token)

        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return ContinueNode.from_token(start_token)
