
from typing import Any
from pylpex.parser.ASTNodes import *
from .exception import ExecutionError


class BreakException(Exception):
    """Exception pour gérer l'instruction break"""
    pass


class ContinueException(Exception):
    """Exception pour gérer l'instruction continue"""
    pass


class StatementsMixin:

    def visit_IfNode(self, node: IfNode) -> Any:
        """Évalue une condition if/else"""
        condition = self.visit(node.condition)
        
        if condition:
            result = None
            for statement in node.then_block:
                result = self.visit(statement)
            return result
        elif node.else_block:
            result = None
            for statement in node.else_block:
                result = self.visit(statement)
            return result
        
        return None
    

    def visit_BreakNode(self, node: BreakNode) -> None:
        """Gère l'instruction break"""
        raise BreakException()
    

    def visit_ContinueNode(self, node: ContinueNode) -> None:
        """Gère l'instruction continue"""
        raise ContinueException()
    

    def visit_WhileNode(self, node: WhileNode) -> None:
        """Évalue une boucle while"""
        try:
            while self.visit(node.condition):
                try:
                    for statement in node.body:
                        self.visit(statement)
                except ContinueException:
                    continue
        except BreakException:
            pass
        
        return None
    
    
    def visit_ForNode(self, node: ForNode) -> None:
        """Évalue une boucle for"""
        iterable = self.visit(node.iterable)
        
        try:
            iter(iterable)
        except TypeError:
            raise ExecutionError(f"L'objet de type '{type(iterable).__name__}' n'est pas itérable", node)
        
        try:
            for value in iterable:
                self.current_env.define(node.variable, value)
                try:
                    for statement in node.body:
                        self.visit(statement)
                except ContinueException:
                    continue
        except BreakException:
            pass
        
        return None