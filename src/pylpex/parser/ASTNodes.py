
from typing import List, Optional, Union, Any
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from pylpex.lexer import Token

# -----------------------------------------------------
# Abstract base class

@dataclass
class ASTNode(ABC):
    """Classe de base pour tous les nœuds de l'arbre syntaxique"""
    position: Optional[tuple[int, int]] = field(default=None, kw_only=True)  # (line, column)
    
    @classmethod
    def from_token(cls, token: Token, **kwargs):
        """Factory method pour créer un node avec position du token"""
        return cls(**kwargs, position=(token.line, token.column))
    
    @property
    def line(self) -> Optional[int]:
        """Ligne de la position du node"""
        return self.position[0] if self.position else None
    
    @property
    def column(self) -> Optional[int]:
        """Colonne de la position du node"""
        return self.position[1] if self.position else None


class TypeEnum(Enum):
    """Clear representation of types"""
    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


# -----------------------------------------------------
# Program structure


@dataclass
class ProgramNode(ASTNode):
    """Nœud racine du programme"""
    statements: List[ASTNode]


@dataclass
class CommentNode(ASTNode):
    """Nœud pour les commentaires (optionnel, peut être ignoré)"""
    text: str

# -----------------------------------------------------
# Data types


@dataclass
class NoneNode(ASTNode):
    """Nœud pour la valeur None"""


class NumberType(TypeEnum):
    INTEGER = "integer"
    FLOAT = "float"

@dataclass
class NumberNode(ASTNode):
    """Nœud pour les nombres (entiers, flottants, complexes)"""
    value: Union[int, float]
    type: NumberType


@dataclass
class StringNode(ASTNode):
    """Nœud pour les chaînes de caractères"""
    value: str


@dataclass
class BooleanNode(ASTNode):
    """Nœud pour les booléens"""
    value: bool


@dataclass
class ListNode(ASTNode):
    """Nœud pour les listes"""
    elements: List[ASTNode]


@dataclass
class DictionaryNode(ASTNode):
    """Nœud pour les dictionnaires"""
    pairs: List[tuple[ASTNode, ASTNode]]  # [(key, value), ...]
    

# -----------------------------------------------------
# Identifiers


@dataclass
class IdentifierNode(ASTNode):
    """Nœud pour les identifiants (variables)"""
    name: str


class AssignmentOperatorType(TypeEnum):
    ASSIGN = "="
    PLUS = "+="
    MINUS = "-="
    MUL = "*="
    DIV = "/="
    POWER = "**="
    MOD = "%="

@dataclass
class AssignmentNode(ASTNode):
    """Nœud pour les assignations (=, +=, -=, etc.)"""
    target: ASTNode  # nom de la variable
    operator: AssignmentOperatorType  # '=', '+=', '-=', etc.
    value: ASTNode

# -----------------------------------------------------
# Operations

class BinaryOperatorType(TypeEnum):
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    POWER = "**"
    MOD = "%"
    AND = "and"
    OR = "or"
    EQ = "=="
    NEQ = "!="
    LT = "<"
    GT = ">"
    LTE = "<="
    GTE = ">="
    IN = "in"
    NOT_IN = "not in"
    IS = "is"
    NOT_IS = "is not"

class UnaryOperatorType(TypeEnum):
    POSITIVE = "+"
    NEGATIVE = "-"
    NOT = "not"

@dataclass
class TernaryNode(ASTNode):
    """Nœud pour les opérations conditionnelles (a if cond else b)"""
    condition: ASTNode
    true_expr: ASTNode
    false_expr: ASTNode


@dataclass
class BinaryOpNode(ASTNode):
    """Nœud pour les opérations binaires (+, -, *, /, etc.)"""
    left: ASTNode
    operator: BinaryOperatorType
    right: ASTNode


@dataclass
class UnaryOpNode(ASTNode):
    """Nœud pour les opérations unaires (-, +, not)"""
    operator: UnaryOperatorType
    operand: ASTNode

# -----------------------------------------------------
# Expressions

@dataclass
class ArgumentNode(ASTNode):
    """Argument d'appel de fonction (positionnel ou nommé)"""
    name: Optional[str]  # None pour les positionnels
    value: ASTNode 

@dataclass
class CallNode(ASTNode):
    """Nœud pour les appels de fonction ( f(a, b) )"""
    function: Union[str, ASTNode] # support pour "obj.foo()"
    arguments: List[ArgumentNode]


@dataclass
class IndexNode(ASTNode):
    """Nœud pour l'indexation (tableaux, chaînes A[i])"""
    collection: ASTNode
    index: ASTNode


@dataclass
class AttributeNode(ASTNode):
    """Nœud pour l'accès aux attributs (obj.attr)"""
    object: ASTNode
    attribute: str


# -----------------------------------------------------
# Statements

@dataclass
class ParameterNode(ASTNode):
    """Paramètre de fonction, possiblement avec valeur par défaut"""
    name: str
    default_value: Optional[ASTNode] = None

@dataclass
class FunctionDefNode(ASTNode):
    """Nœud pour les définitions de fonctions"""
    name: str
    parameters: List[ParameterNode]
    body: List[ASTNode]

@dataclass
class ReturnNode(ASTNode):
    """Nœud pour les retours de fonction"""
    value: Optional[ASTNode]


@dataclass
class IfNode(ASTNode):
    """Nœud pour les conditions if/else"""
    condition: ASTNode
    then_block: List[ASTNode]
    else_block: Optional[List[ASTNode]]


@dataclass
class WhileNode(ASTNode):
    """Nœud pour les boucles while"""
    condition: ASTNode
    body: List[ASTNode]


@dataclass
class ForNode(ASTNode):
    """Nœud pour les boucles for"""
    variable: str
    iterable: ASTNode
    body: List[ASTNode]


@dataclass
class BreakNode(ASTNode):
    """Nœud pour l'instruction break"""


@dataclass
class ContinueNode(ASTNode):
    """Nœud pour l'instruction continue"""