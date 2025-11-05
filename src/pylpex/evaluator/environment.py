from .exception import ExecutionError

class Environment:
    """Représente un environnement d'exécution (scope lexical)"""
    def __init__(self, parent: 'Environment' = None):
        self.vars = {}
        self._types = {}
        self.parent = parent

    def define(self, name: str, value):
        self.vars[name] = value

    def assign(self, name: str, value):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise ExecutionError(f"Variable '{name}' non définie")

    def lookup(self, name: str):
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent.lookup(name)
        else:
            raise ExecutionError(f"Variable '{name}' non définie")
        
    def set_type(self, name, type_info):
        self._types[name] = type_info

    def get_type(self, name):
        if name in self._types:
            return self._types[name]
        if self.parent:
            return self.parent.get_type(name)
        return None
        
    def __repr__(self):
        return f"Environment({self.vars}, parent={self.parent})"
