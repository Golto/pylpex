
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

# TODO rajouter la position (line, column) dans les nodes pour les erreurs

class Parser:

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
    }

    UNARY_TOKEN_TO_ENUM = {
        TokenType.PLUS: UnaryOperatorType.POSITIVE,
        TokenType.MINUS: UnaryOperatorType.NEGATIVE,
        TokenType.NOT: UnaryOperatorType.NOT,
    }

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.loop_depth = 0 # loop context (for break/continue)
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

            node = AssignmentNode(
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
    

    def parse_expression(self, min_prec: int = 0) -> ASTNode:
        """Pratt / precedence climbing expression parser that also handles ternary"""
        self.skip_whitespace_and_comments()
        left = self.parse_unary_or_primary()

        # TODO while loop, binops, ternary
        while True:
            self.skip_whitespace_and_comments()
            token = self.current_token
            if not token:
                break

            # <true_expr> if <cond> else <false_expr>
            if token.type == TokenType.IF:
                self.advance()  # consume 'if'
                cond = self.parse_expression()
                self.skip_whitespace_and_comments()
                if not self.current_token or self.current_token.type != TokenType.ELSE:
                    raise ParseError("Ternary 'if' sans 'else'", token)
                self.advance()  # consume 'else'
                false_expr = self.parse_expression()
                left = TernaryNode(condition=cond, true_expr=left, false_expr=false_expr)
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
                    raise ParseError(f"Opérateur binaire non-supporté: {token.type}", token)
                left = BinaryOpNode(left=left, operator=binop, right=right)
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
            return UnaryOpNode(operator=op, operand=operand)
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
                    node = CallNode(function=node.name, arguments=args)
                else:
                    node = CallNode(function=repr(node), arguments=args)
                continue

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

    
    def parse_argument_list(self) -> List[ArgumentNode]:
        """Parse les arguments d'appel de fonction (f(a, b, x=4))"""
        args = []
        self.expect(TokenType.LPAREN)
        self.skip_whitespace_and_comments()

        if self.current_token and self.current_token.type != TokenType.RPAREN:
            while True:
                expr = self.parse_expression()
                # If a '=' follows, it is a named argument
                if isinstance(expr, IdentifierNode) and self.current_token and self.current_token.type == TokenType.ASSIGN:
                    self.advance()  # consomme '='
                    value = self.parse_expression()
                    args.append(ArgumentNode(name=expr.name, value=value))
                else:
                    args.append(ArgumentNode(name=None, value=expr))

                self.skip_whitespace_and_comments()
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                    self.skip_whitespace_and_comments()
                    continue
                break

        self.expect(TokenType.RPAREN)
        return args

    
    # --------------------
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
    

    def parse_if(self) -> IfNode:
        self.expect(TokenType.IF)
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
        return IfNode(condition=cond, then_block=then_block, else_block=else_block)


    def parse_while(self) -> WhileNode:
        self.expect(TokenType.WHILE)
        cond = self.parse_expression()
        self.skip_whitespace_and_comments()

        self.loop_depth += 1
        if self.current_token and self.current_token.type == TokenType.LBRACE:
            body = self.parse_block()
        else:
            stmt = self.parse_statement()
            body = [stmt] if stmt else []
        self.loop_depth -= 1

        return WhileNode(condition=cond, body=body)
    

    def parse_for(self) -> ForNode:
        """Parse une boucle for (for x in iterable { ... })"""
        self.expect(TokenType.FOR)

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

        return ForNode(variable=var_name, iterable=iterable_expr, body=body)

    

    def parse_parameter_list(self) -> List[ParameterNode]:
        """Parse la liste des paramètres d'une fonction"""
        params = []
        self.expect(TokenType.LPAREN)
        self.skip_whitespace_and_comments()

        if self.current_token and self.current_token.type != TokenType.RPAREN:
            while True:
                if self.current_token.type != TokenType.IDENTIFIER:
                    raise ParseError("Nom de paramètre attendu", self.current_token)
                name = self.current_token.value
                self.advance()
                default_value = None
                # valeur par défaut : " = expression"
                if self.current_token and self.current_token.type == TokenType.ASSIGN:
                    self.advance()
                    default_value = self.parse_expression()
                params.append(ParameterNode(name=name, default_value=default_value))

                self.skip_whitespace_and_comments()
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                    self.skip_whitespace_and_comments()
                    continue
                break

        self.expect(TokenType.RPAREN)
        return params


    def parse_function_def(self) -> FunctionDefNode:
        self.expect(TokenType.FUNCTION)
        if not (self.current_token and self.current_token.type == TokenType.IDENTIFIER):
            raise ParseError("Nom de fonction attendu", self.current_token)
        name = self.current_token.value
        self.advance()
        params = self.parse_parameter_list()
        self.skip_whitespace_and_comments()
        body = self.parse_block()
        return FunctionDefNode(name=name, parameters=params, body=body)



    def parse_return(self) -> ReturnNode:
        self.expect(TokenType.RETURN)
        # optional expression
        if self.current_token and self.current_token.type not in (TokenType.SEMICOLON, TokenType.NEWLINE, TokenType.EOF, TokenType.RBRACE):
            val = self.parse_expression()
        else:
            val = None
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return ReturnNode(value=val)
    

    def parse_break(self) -> BreakNode:
        """Parse l'instruction 'break'"""
        self.expect(TokenType.BREAK)
        if self.loop_depth == 0:
            raise ParseError("'break' ne peut être utilisé qu'à l'intérieur d'une boucle", self.current_token)

        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return BreakNode()


    def parse_continue(self) -> ContinueNode:
        """Parse l'instruction 'continue'"""
        self.expect(TokenType.CONTINUE)
        if self.loop_depth == 0:
            raise ParseError("'continue' ne peut être utilisé qu'à l'intérieur d'une boucle", self.current_token)

        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return ContinueNode()

    

    # -----------------------------------------------------
    # Helper methods

    def __repr__(self):
        return f"<Parser position={self.position} current_token={self.current_token}>"