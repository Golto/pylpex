
from src.parser.ASTNodes import ASTNode

class ASTVisitor:
    def visit(self, node: ASTNode):
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"Aucune méthode visit_{type(node).__name__}")