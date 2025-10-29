# pylpex/typesystem.py
from typing import List, Optional, Union
from enum import Enum

class BaseType(Enum):
    # Data types
    NONE = "null"
    INTEGER = "int"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "bool"
    LIST = "list"
    DICTIONARY = "dict"
    CALLABLE = "callable"
    # Type constructors
    UNION = "union"
    OPTIONAL = "optional"
    ARGS = "args"
    VARIADIC = "variadic" # for variadic arguments *args
    KW_VARIADIC = "kw_variadic" # for variadic keyword arguments **kwargs
    # Special types
    ANY = "any"  # non strict typing

class TypeInfo:
    """Représente un type dans le système Pylpex."""
    def __init__(self, base: BaseType, subtypes: Optional[Union['TypeInfo', List['TypeInfo']]] = None):
        self.base = base
        # subtypes est soit None, soit un TypeInfo unique, soit une liste de TypeInfo
        if isinstance(subtypes, TypeInfo):
            self.subtypes = [subtypes]
        elif isinstance(subtypes, list):
            self.subtypes = subtypes
        else:
            self.subtypes = None

    def __repr__(self):
        if self.subtypes:
            inner = ", ".join(repr(s) for s in self.subtypes)
            return f"{self.base.value}[{inner}]"
        return self.base.value

    def __eq__(self, other):
        if not isinstance(other, TypeInfo):
            return False
        return self.base == other.base and self.subtypes == other.subtypes
    
    @classmethod
    def union(cls, *types: 'TypeInfo') -> 'TypeInfo':
        """Crée un type union simplifié à partir de plusieurs TypeInfo."""
        flattened = []

        for t in types:
            if t is None:
                continue
            # Aplatir les unions imbriquées : union[union[int, string], bool] -> [int, string, bool]
            if t.base == BaseType.UNION and t.subtypes:
                flattened.extend(t.subtypes)
            else:
                flattened.append(t)

        # Supprimer les doublons (en comparant base + sous-types)
        unique_types = []
        for t in flattened:
            if not any(t == u for u in unique_types):
                unique_types.append(t)

        # Si vide, renvoyer ANY
        if not unique_types:
            return cls(BaseType.ANY)

        # Si un seul type, inutile d'avoir UNION
        if len(unique_types) == 1:
            return unique_types[0]

        # Si tous les types sont égaux → pas besoin d’union non plus
        if all(t == unique_types[0] for t in unique_types):
            return unique_types[0]

        return cls(BaseType.UNION, unique_types)
    
    @classmethod
    def callable(cls, arg_types: List['TypeInfo'], return_type: 'TypeInfo') -> 'TypeInfo':
        """Crée un type callable avec les types d'arguments et le type de retour."""
        args = cls(BaseType.ARGS, arg_types)
        return cls(BaseType.CALLABLE, [args, return_type])