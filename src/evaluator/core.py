
from typing import Optional
from src.parser.ASTNodes import *
from .environment import Environment, RuntimeErrorEx
from .visitor import ASTVisitor

class Evaluator(ASTVisitor):
    """Évalue l'AST dans un environnement donné"""

    def __init__(self, global_env: Optional[Environment] = None):
        self.global_env = global_env or Environment()
        self.current_env = self.global_env

    def evaluate(self, node: ASTNode) -> Any:
        """Point d'entrée principal pour évaluer un AST"""
        return self.visit(node)
    
    # -------------------------------
    # Program structure

    def visit_ProgramNode(self, node: ProgramNode) -> Any:
        """Évalue un programme complet"""
        result = None
        for statement in node.statements:
            result = self.visit(statement)
        return result

    # -------------------------------
    # Literals

    def visit_NoneNode(self, node: NoneNode) -> None:
        return None

    def visit_NumberNode(self, node: NumberNode) -> Union[int, float]:
        return node.value

    def visit_StringNode(self, node: StringNode) -> str:
        return node.value

    def visit_BooleanNode(self, node: BooleanNode) -> bool:
        return node.value

    def visit_ListNode(self, node: ListNode) -> List[Any]:
        return [self.visit(elem) for elem in node.elements]
    
    def visit_DictionaryNode(self, node: DictionaryNode) -> dict:
        result = {}
        for key_node, value_node in node.pairs:
            if isinstance(key_node, StringNode):
                key = key_node.value
                value = self.visit(value_node)
                result[key] = value
            else:
                # key = self.visit(key_node) # TODO faire une erreur propre
                raise RuntimeErrorEx(f"Clé de dictionnaire non hashable: {type(key).__name__}", node)
            
        return result

    # -------------------------------
    # Variables

    def visit_IdentifierNode(self, node: IdentifierNode) -> Any:
        try:
            return self.current_env.lookup(node.name)
        except RuntimeErrorEx:
            raise RuntimeErrorEx(f"Variable '{node.name}' non définie", node)

    def visit_AssignmentNode(self, node: AssignmentNode) -> Any:
        value = self.visit(node.value)

        if isinstance(node.target, IdentifierNode):
            # Assignation simple: x = 5
            if node.operator == AssignmentOperatorType.ASSIGN:
                self.current_env.define(node.target.name, value)
            else:
                # Opérateurs composés: +=, -=, etc.
                try:
                    current = self.current_env.lookup(node.target.name)
                except RuntimeErrorEx:
                    raise RuntimeErrorEx(f"Variable '{node.target.name}' non définie", node)
                
                if node.operator == AssignmentOperatorType.PLUS:
                    value = current + value
                elif node.operator == AssignmentOperatorType.MINUS:
                    value = current - value
                elif node.operator == AssignmentOperatorType.MUL:
                    value = current * value
                elif node.operator == AssignmentOperatorType.DIV:
                    value = current / value
                elif node.operator == AssignmentOperatorType.POWER:
                    value = current ** value
                elif node.operator == AssignmentOperatorType.MOD:
                    value = current % value
                
                self.current_env.assign(node.target.name, value)

        elif isinstance(node.target, IndexNode):
            # Assignation à un index: lst[0] = 5
            collection = self.visit(node.target.collection)
            index = self.visit(node.target.index)
            
            # TODO implémenter les opérateurs composés pour les index
            if node.operator != AssignmentOperatorType.ASSIGN:
                raise RuntimeErrorEx("Les opérateurs composés ne sont pas supportés pour l'indexation", node)
            
            try:
                collection[index] = value
            except (TypeError, KeyError, IndexError) as e:
                raise RuntimeErrorEx(f"Erreur d'assignation: {e}", node)
            
        
        # TODO : Ajouter le cas pour les attributs (x.y = 5) 
        else:
            raise RuntimeErrorEx(f"Target d'assignation invalide: {type(node.target).__name__}", node)
        
        return value

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
                    raise RuntimeErrorEx("Division par zéro", node) # FIXME double erreur : RuntimeErrorEx: Erreur à la ligne 2, colonne 3: Erreur d'opération: Erreur à la ligne 2, colonne 3: Division par zéro
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
            raise RuntimeErrorEx(f"Erreur d'opération: {e}", node)

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
            raise RuntimeErrorEx(f"Erreur d'opération unaire: {e}", node)
    
    # -------------------------------
    # Opérateur ternaire

    def visit_TernaryNode(self, node: TernaryNode) -> Any:
        condition = self.visit(node.condition)
        if condition:
            return self.visit(node.true_expr)
        else:
            return self.visit(node.false_expr)

    # -------------------------------
    # Expressions

    def visit_IndexNode(self, node: IndexNode) -> Any:
        collection = self.visit(node.collection)
        index = self.visit(node.index)
        # TODO test de index NumberNode & index.type = NumberType.Integer
        try:
            return collection[index]
        except (TypeError, KeyError, IndexError) as e:
            # FIXME Faire des erreurs customs, pas de Python
            raise RuntimeErrorEx(f"Erreur d'indexation: {e}", node)
    
    # FIXME: changer type(obj).__name__ pour quelque chose qui reste au sein du langage
    # TODO: implémneter la possibilité de donner des attributes à des objets
    def visit_AttributeNode(self, node: AttributeNode) -> Any:
        obj = self.visit(node.object)
        
        try:
            return getattr(obj, node.attribute)
        except AttributeError:
            raise RuntimeErrorEx(
                f"L'objet de type '{type(obj).__name__}' n'a pas d'attribut '{node.attribute}'",
                node
            )
    
    # -------------------------------
    # Structures de contrôle

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
    
    # TODO revoir à partir d'ici
    # cf https://claude.ai/chat/c3c0e176-7157-425e-9a19-e0861076252f
    # -------------------------------
    # Fonctions

    # TODO

    # -------------------------------
    # Blocs et structures

    def visit_block(self, stmts):
        result = None
        prev_env = self.current_env
        self.current_env = Environment(parent=prev_env)
        try:
            for stmt in stmts:
                result = self.visit(stmt)
        finally:
            self.current_env = prev_env
        return result

    # -------------------------------
    # Appels de fonction

    def visit_CallNode(self, node):
        func = self.visit(node.function) if not isinstance(node.function, str) else self.current_env.lookup(node.function)
        if not callable(func):
            raise RuntimeErrorEx(f"'{node.function}' n’est pas une fonction", node)
        args = [self.visit(arg.value) for arg in node.arguments]
        return func(*args)
