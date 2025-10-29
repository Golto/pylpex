
from typing import Any
from pylpex.parser.ASTNodes import (
    UnaryOpNode, UnaryOperatorType,
    BinaryOpNode, BinaryOperatorType, 
    TernaryNode
)
from .exception import ExecutionError


class OperatorsMixin:

    # -------------------------------
    # Opérateurs binaires

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> Any:
        left = self.visit(node.left)
        
        # Court-circuit pour 'and' et 'or'
        if node.operator == BinaryOperatorType.AND:
            if not left:
                return left
            return self.visit(node.right)
        elif node.operator == BinaryOperatorType.OR:
            if left:
                return left
            return self.visit(node.right)
        
        right = self.visit(node.right)
        
        try:
            if node.operator == BinaryOperatorType.PLUS:
                return left + right
            elif node.operator == BinaryOperatorType.MINUS:
                return left - right
            elif node.operator == BinaryOperatorType.MUL:
                return left * right
            elif node.operator == BinaryOperatorType.DIV:
                if right == 0:
                    raise ExecutionError("Division par zéro", node) # FIXME double erreur : ExecutionError: Erreur à la ligne 2, colonne 3: Erreur d'opération: Erreur à la ligne 2, colonne 3: Division par zéro
                return left / right
            elif node.operator == BinaryOperatorType.POWER:
                return left ** right
            elif node.operator == BinaryOperatorType.MOD:
                return left % right
            elif node.operator == BinaryOperatorType.EQ:
                return left == right
            elif node.operator == BinaryOperatorType.NEQ:
                return left != right
            elif node.operator == BinaryOperatorType.LT:
                return left < right
            elif node.operator == BinaryOperatorType.GT:
                return left > right
            elif node.operator == BinaryOperatorType.LTE:
                return left <= right
            elif node.operator == BinaryOperatorType.GTE:
                return left >= right
            elif node.operator == BinaryOperatorType.IN:
                return left in right
            elif node.operator == BinaryOperatorType.NOT_IN:
                return left not in right
        except Exception as e:
            raise ExecutionError(f"Erreur d'opération: {e}", node)

    # -------------------------------
    # Opérateurs unaires

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> Any:
        operand = self.visit(node.operand)
        
        try:
            if node.operator == UnaryOperatorType.POSITIVE:
                return +operand
            elif node.operator == UnaryOperatorType.NEGATIVE:
                return -operand
            elif node.operator == UnaryOperatorType.NOT:
                return not operand
        except Exception as e:
            raise ExecutionError(f"Erreur d'opération unaire: {e}", node)
    
    # -------------------------------
    # Opérateur ternaire

    def visit_TernaryNode(self, node: TernaryNode) -> Any:
        condition = self.visit(node.condition)
        if condition:
            return self.visit(node.true_expr)
        else:
            return self.visit(node.false_expr)