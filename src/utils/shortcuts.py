from typing import List, Any
from src.lexer import Lexer, Token
from src.parser import Parser, ASTNode
from src.evaluator import Evaluator

def tokenize(code: str) -> List[Token]:
    lexer = Lexer(code)
    return lexer.tokenize()

def parse(code: str) -> ASTNode:
    tokens = tokenize(code)
    parser = Parser(tokens)
    return parser.parse()

def evaluate(code: str) -> Any:
    ast = parse(code)
    evaluator = Evaluator()
    return evaluator.evaluate(ast)