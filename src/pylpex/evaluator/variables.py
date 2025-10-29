
from typing import Any
from pylpex.parser.ASTNodes import *
from .exception import ExecutionError

class VariablesMixin:

    def visit_IdentifierNode(self, node: IdentifierNode) -> Any:
        try:
            return self.current_env.lookup(node.name)
        except ExecutionError:
            raise ExecutionError(f"Variable '{node.name}' non définie", node)

    def _apply_compound_operator(self, operator: AssignmentOperatorType, current: Any, value: Any, node: ASTNode) -> Any:
        """Applique un opérateur composé (+=, -=, etc.) et retourne la nouvelle valeur"""
        try:
            if operator == AssignmentOperatorType.PLUS:
                return current + value
            elif operator == AssignmentOperatorType.MINUS:
                return current - value
            elif operator == AssignmentOperatorType.MUL:
                return current * value
            elif operator == AssignmentOperatorType.DIV:
                if value == 0:
                    raise ExecutionError("Division par zéro", node)
                return current / value
            elif operator == AssignmentOperatorType.POWER:
                return current ** value
            elif operator == AssignmentOperatorType.MOD:
                return current % value
            else:
                raise ExecutionError(f"Opérateur composé inconnu: {operator}", node)
        except Exception as e:
            raise ExecutionError(f"Erreur d'opération: {e}", node)
        
    def visit_AssignmentNode(self, node: AssignmentNode) -> Any:
        value = self.visit(node.value)

        if isinstance(node.target, IdentifierNode):
            # Assignation à une variable: x = 5 ou x += 5
            if node.operator == AssignmentOperatorType.ASSIGN:
                self.current_env.define(node.target.name, value)
            else:
                # Opérateurs composés: +=, -=, etc.
                try:
                    current = self.current_env.lookup(node.target.name)
                except ExecutionError:
                    raise ExecutionError(f"Variable '{node.target.name}' non définie", node)
                
                value = self._apply_compound_operator(node.operator, current, value, node)
                self.current_env.assign(node.target.name, value)
        
        elif isinstance(node.target, IndexNode):
            # Assignation à un index: lst[0] = 5 ou lst[0] += 5
            collection = self.visit(node.target.collection)
            index = self.visit(node.target.index)
            
            if node.operator == AssignmentOperatorType.ASSIGN:
                try:
                    collection[index] = value
                except (TypeError, KeyError, IndexError) as e:
                    raise ExecutionError(f"Erreur d'assignation: {e}", node)
            else:
                # Opérateurs composés
                try:
                    current = collection[index]
                except (TypeError, KeyError, IndexError) as e:
                    raise ExecutionError(f"Erreur de lecture: {e}", node)
                
                value = self._apply_compound_operator(node.operator, current, value, node)
                
                try:
                    collection[index] = value
                except (TypeError, KeyError, IndexError) as e:
                    raise ExecutionError(f"Erreur d'assignation: {e}", node)
            
        
        # TODO : Ajouter le cas pour les attributs (x.y = 5) 
        else:
            raise ExecutionError(f"Target d'assignation invalide: {type(node.target).__name__}", node)
        
        return value