
from typing import Optional
from src.parser.ASTNodes import ASTNode

class RuntimeErrorEx(Exception):
    def __init__(self, message: str, node: Optional[ASTNode] = None):
        if node and node.position:
            line, col = node.position
            super().__init__(f"Erreur à la ligne {line}, colonne {col}: {message}")
        else:
            super().__init__(message)


class Environment:
    """Représente un environnement d'exécution (scope lexical)"""
    def __init__(self, parent: 'Environment' = None):
        self.vars = {}
        self.parent = parent

    def define(self, name: str, value):
        self.vars[name] = value

    def assign(self, name: str, value):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise RuntimeErrorEx(f"Variable '{name}' non définie")

    def lookup(self, name: str):
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent.lookup(name)
        else:
            raise RuntimeErrorEx(f"Variable '{name}' non définie")
