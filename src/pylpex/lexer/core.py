
from typing import List, Optional
from .tokens import Token, TokenType


class LexicalError(Exception):
    """Erreur lexicale détectée pendant l'analyse lexicale"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Erreur lexicale à la ligne {line}, colonne {column}: {message}")


class Lexer:

    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.current_char: Optional[str] = self.source[0] if source else None

        self.keywords = {
            # Data types
            'none': TokenType.NONE,
            'true': TokenType.BOOLEAN,
            'false': TokenType.BOOLEAN,
            # Logical operators
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
            # Keywords
            'def': TokenType.FUNCTION, # NOTE Python heritage
            'function': TokenType.FUNCTION,
            'return': TokenType.RETURN,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'in': TokenType.IN,
            'break': TokenType.BREAK,
            'continue': TokenType.CONTINUE,
        }

    # -----------------------------------------------------
    # Common methods

    def advance(self):
        """Avance d'un caractère dans le code source"""
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        self.position += 1
        self.current_char = self.source[self.position] if self.position < len(self.source) else None

    def peek(self, offset: int = 1) -> Optional[str]:
        """Regarde le caractère à une position future sans avancer"""
        peek_position = self.position + offset
        return self.source[peek_position] if peek_position < len(self.source) else None
    
    # -----------------------------------------------------
    # Reading methods

    def skip_whitespace(self):
        """Ignore les espaces et tabulations (mais pas les retours à la ligne)"""
        while self.current_char and self.current_char in ' \t\r':
            self.advance()

    def read_comment(self) -> Optional[Token]:
        """Lit les commentaires (// une ligne ou /* bloc */)"""
        start_line = self.line
        start_column = self.column
        
        # Commentaire sur une ligne //
        if self.current_char == '/' and self.peek() == '/':
            self.advance()  # premier /
            self.advance()  # deuxième /
            comment = ''
            while self.current_char and self.current_char != '\n':
                comment += self.current_char
                self.advance()
            return Token(TokenType.COMMENT, comment.strip(), start_line, start_column, _actual_value=f"//{comment}")
        
        # Commentaire bloc /* ... */
        elif self.current_char == '/' and self.peek() == '*':
            self.advance()  # /
            self.advance()  # *
            comment = ''
            while self.current_char:
                if self.current_char == '*' and self.peek() == '/':
                    self.advance()  # *
                    self.advance()  # /
                    break
                comment += self.current_char
                self.advance()
            else:
                raise LexicalError("Commentaire bloc non terminé", start_line, start_column)
            return Token(TokenType.COMMENT, comment.strip(), start_line, start_column, _actual_value=f"/*{comment}*/")
        
        return None

    def read_number(self) -> Token:
        """Lit un nombre (entier, flottant ou complexe)"""
        start_line = self.line
        start_column = self.column
        num_str = ''
        has_dot = False
        
        while self.current_char and (self.current_char.isdigit() or self.current_char in '._'):
            if self.current_char == '.':
                if has_dot:
                    break
                has_dot = True
                num_str += self.current_char
                self.advance()
            elif self.current_char == '_':
                # Permet les underscores dans les nombres (ex: 1_000_000)
                self.advance()
            else:
                num_str += self.current_char
                self.advance()
        
        if has_dot:
            return Token(TokenType.FLOAT, num_str, start_line, start_column)
        else:
            return Token(TokenType.INTEGER, num_str, start_line, start_column)
    
    def read_string(self, quote_char: str) -> Token:
        """Lit une chaîne de caractères"""
        start_line = self.line
        start_column = self.column
        self.advance()  # Skip opening quote

        value = ''
        while self.current_char and self.current_char != quote_char:
            if self.current_char == '\\':
                self.advance()
                if self.current_char in 'ntr\'"\\':
                    escape_chars = {'n': '\n', 't': '\t', 'r': '\r', '"': '"', "'": "'", '\\': '\\'}
                    value += escape_chars.get(self.current_char, self.current_char)
                    self.advance()
                else:
                    value += self.current_char
                    self.advance()
            else:
                value += self.current_char
                self.advance()

        self.advance()  # Skip closing quote
        return Token(TokenType.STRING, value, start_line, start_column, _actual_value=f"{quote_char}{value}{quote_char}")
    
    def read_identifier(self) -> Token:
        """Lit un identifiant ou mot-clé"""
        start_line = self.line
        start_column = self.column
        value = ''
        
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            value += self.current_char
            self.advance()
        
        # Vérifie si c'est un mot-clé
        token_type = self.keywords.get(value, TokenType.IDENTIFIER)
        return Token(token_type, value, start_line, start_column)

    # -----------------------------------------------------
    # Tokenisation methods

    def get_next_token(self) -> Token:
        """Retourne le prochain token"""
        while self.current_char:
            # Ignore les espaces
            if self.current_char in ' \t\r':
                self.skip_whitespace()
                continue

            # Commentaires
            if self.current_char == '/':
                next_char = self.peek()
                if next_char == '/' or next_char == '*':
                    comment = self.read_comment()
                    if comment is None:
                        continue
                    return comment

            # Nouvelle ligne
            if self.current_char == '\n':
                token = Token(TokenType.NEWLINE, '\\n', self.line, self.column, _actual_value='\n')
                self.advance()
                return token
            
            # Nombres
            if self.current_char.isdigit():
                return self.read_number()
            
            # Chaînes de caractères
            if self.current_char in '"\'':
                return self.read_string(self.current_char)
            
            # Identifiants et mots-clés
            if self.current_char.isalpha() or self.current_char == '_':
                return self.read_identifier()
            
            # Opérateurs et délimiteurs
            line, col = self.line, self.column
            char = self.current_char

            # Opérateurs d'assignation composés
            if char == '+' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.PLUS_ASSIGN, '+=', line, col)
            
            if char == '-' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.MINUS_ASSIGN, '-=', line, col)
            
            if char == '*' and self.peek() == '*' and self.peek(2) == '=':
                self.advance()
                self.advance()
                self.advance()
                return Token(TokenType.POWER_ASSIGN, '**=', line, col)
            
            if char == '*' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.MUL_ASSIGN, '*=', line, col)
            
            if char == '/' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.DIV_ASSIGN, '/=', line, col)
            
            if char == '%' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.MOD_ASSIGN, '%=', line, col)
            
            # Opérateurs de comparaison
            if char == '=' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.EQ, '==', line, col)
            
            if char == '!' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.NEQ, '!=', line, col)
            
            if char == '<' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.LTE, '<=', line, col)
            
            if char == '>' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.GTE, '>=', line, col)
            
            # Opérateur d'exponentiation
            if char == '*' and self.peek() == '*':
                self.advance()
                self.advance()
                return Token(TokenType.POWER, '**', line, col)
            
            # Opérateurs simples
            single_char_tokens = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MUL,
                '/': TokenType.DIV,
                '%': TokenType.MOD,
                '=': TokenType.ASSIGN,
                '<': TokenType.LT,
                '>': TokenType.GT,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '}': TokenType.RBRACE,
                '{': TokenType.LBRACE,
                ']': TokenType.RBRACKET,
                '[': TokenType.LBRACKET,
                ',': TokenType.COMMA,
                ';': TokenType.SEMICOLON,
                ':': TokenType.COLON,
                '.': TokenType.DOT,
            }

            # Flèche de typage ->
            if char == '-' and self.peek() == '>':
                self.advance()
                self.advance()
                return Token(TokenType.ARROW, '->', line, col)
            
            if char in single_char_tokens:
                token_type = single_char_tokens[char]
                self.advance()
                return Token(token_type, char, line, col)

            raise LexicalError(f"Caractère inattendu '{char}'", line, col)

        return Token(TokenType.EOF, '', self.line, self.column)

    def tokenize(self) -> List[Token]:
        """Tokenise tout le code source"""
        tokens = []
        token = self.get_next_token()
        
        while token.type != TokenType.EOF:
            # Ignore les nouvelles lignes multiples
            if token.type == TokenType.NEWLINE:
                if not tokens or tokens[-1].type != TokenType.NEWLINE:
                    tokens.append(token)
            else:
                tokens.append(token)
            token = self.get_next_token()
        
        tokens.append(token)  # Add EOF
        return tokens
    
    # -----------------------------------------------------
    # Helper methods

    def __repr__(self):
        return f"<Lexer line={self.line} column={self.column} position={self.position}>"