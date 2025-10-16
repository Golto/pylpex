import json
from dataclasses import asdict

from .ASTNodes import ASTNode

# TODO faire mieux
def ast_print(node: ASTNode, indent: int = 4) -> None:
    """Prints the AST in a readable format"""
    node_dict = asdict(node)
    print(
        json.dumps(node_dict, indent=indent)
    )