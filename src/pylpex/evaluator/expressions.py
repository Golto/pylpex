from typing import Any, List, Union
from .exception import ExecutionError
from pylpex.parser.ASTNodes import *

class ExpressionsMixin:

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
                key = self.visit(key_node)
                key_type = self._infer_type(key)
                raise ExecutionError(f"Clé de dictionnaire non hashable pour le type: {key_type}", node)
            
        return result