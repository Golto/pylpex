from src.lexer import TokenType
from .ASTNodes import ProgramNode
from .expressions import ExpressionParser
from .statements import StatementParser
from .functions import FunctionParser
from .structures import StructureParser

# mixins
class Parser(ExpressionParser, StatementParser, FunctionParser, StructureParser):
    
    def parse(self) -> ProgramNode:
        """Point d'entrée: parse tout le programme"""
        statements = []
        token = self.current_token
        
        self.skip_whitespace_and_comments()
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            self.skip_whitespace_and_comments()
            
            if self.current_token and self.current_token.type != TokenType.EOF:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            
            self.skip_whitespace_and_comments()
        
        return ProgramNode.from_token(token=token, statements=statements)
    
    # -----------------------------------------------------
    # Helper methods

    def __repr__(self):
        return f"<Parser position={self.position} current_token={self.current_token}>"
