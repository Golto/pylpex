
from typing import Optional
from pylpex.parser.ASTNodes import *
from pylpex.typesystem import TypeInfo, BaseType
from .environment import Environment
from .exception import ExecutionError
from .visitor import ASTVisitor
# mixins
from .builtin import BuiltinMixin, BuiltinFunction
from .expressions import ExpressionsMixin
from .variables import VariablesMixin
from .statements import StatementsMixin
from .operators import OperatorsMixin




class ReturnException(Exception):
    """Exception pour gérer l'instruction return"""
    def __init__(self, value):
        self.value = value


class Function:
    """Représente une fonction définie par l'utilisateur"""
    def __init__(self, name: str, parameters: List[ParameterNode], body: List[ASTNode], closure: Environment, return_type: Optional[TypeInfo] = None):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.closure = closure
        self.return_type = return_type
    
    def __repr__(self):
        return f"<function {self.name}>"

mixins = [
    BuiltinMixin,
    ExpressionsMixin,
    VariablesMixin,
    StatementsMixin,
    OperatorsMixin
]

# TODO faire un mode strict pour les types
# self.strict_typing = False -> typage facultatif et ne cause pas d'erreur
# self.strict_typing = True -> typage obligatoire et cause une erreur si non respecté
# cf https://chatgpt.com/g/g-p-68f0432b8c7081918f5e46292e69206b/c/69019e0a-55ec-832b-9cef-8b8f4ef0d9c1

# visit_AssignmentNode
#       strict typing -> vérifier le type déclarée vs le type réelle
#       non strict typing -> pas de vérification
# _call_user_function
#       strict typing -> vérifier le type des arguments vs le type des paramètres
#           si possible, vérifier le type de retour vs le type de la variable de retour
#       non strict typing -> pas de vérification

class Evaluator(ASTVisitor, *mixins):
    """Évalue l'AST dans un environnement donné"""


    def __init__(self, global_env: Optional[Environment] = None, strict_typing = False):
        self.global_env = global_env or Environment()
        self.current_env = self.global_env
        self.strict_typing = strict_typing
        self._setup_builtins()

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
    # Type annotations
    
    def _infer_type(self, value) -> TypeInfo:
        """Infère récursivement le type d'une valeur Python en TypeInfo"""

        if value is None:
            return TypeInfo(BaseType.NONE)

        if isinstance(value, bool):
            return TypeInfo(BaseType.BOOLEAN)

        if isinstance(value, int):
            return TypeInfo(BaseType.INTEGER)

        if isinstance(value, float):
            return TypeInfo(BaseType.FLOAT)

        if isinstance(value, str):
            return TypeInfo(BaseType.STRING)
        
        if isinstance(value, list):
            # Inférer le type des éléments
            if not value:
                subtype = TypeInfo(BaseType.ANY)
            else:
                subtypes = [self._infer_type(v) for v in value]
                subtype = TypeInfo.union(*subtypes)
            return TypeInfo(BaseType.LIST, subtype)
        
        if isinstance(value, dict):
            # Inférer types des clés et valeurs
            if not value:
                key_t = TypeInfo(BaseType.ANY)
                val_t = TypeInfo(BaseType.ANY)
            else:
                key_t = TypeInfo.union(*[self._infer_type(k) for k in value.keys()])
                val_t = TypeInfo.union(*[self._infer_type(v) for v in value.values()])
            return TypeInfo(BaseType.DICTIONARY, [key_t, val_t])
        
        if isinstance(value, Function):
            # Fonction définie par l'utilisateur
            arg_types = [p.type_annotation or TypeInfo(BaseType.ANY) for p in value.parameters]
            ret_type = value.return_type or TypeInfo(BaseType.ANY)
            return TypeInfo.callable(arg_types, ret_type)
        
        if isinstance(value, BuiltinFunction):
            # Fonction native
            arg_types = value.arg_types
            ret_type = value.return_type
            return TypeInfo.callable(arg_types, ret_type)

        return TypeInfo(BaseType.ANY)
    

    def _is_compatible(self, actual: TypeInfo, expected: TypeInfo) -> bool: # TODO implémenter la vérification de compatibilité des typages
        pass

    def _raise_if_incompatible(self, node: ASTNode, ) -> None: # TODO implémenter la levée d'erreurs en cas de conflits de types
        pass

    # -------------------------------
    # Expressions

    def visit_IndexNode(self, node: IndexNode) -> Any:
        collection = self.visit(node.collection)
        index = self.visit(node.index)
        
        # Vérifications selon le type de collection
        if isinstance(collection, list):
            # Pour les listes : l'index doit être un entier
            if not isinstance(index, int):
                index_type = self._infer_type(index)
                raise ExecutionError(
                    f"Les indices de liste doivent être des entiers, pas '{index_type}'",
                    node
                )
            
            # Vérifier les bornes
            if index < 0:
                # Support des indices négatifs comme en Python
                actual_index = len(collection) + index
                if actual_index < 0:
                    raise ExecutionError(
                        f"Index de liste hors limites: {index} (longueur: {len(collection)})",
                        node
                    )
                return collection[actual_index]
            elif index >= len(collection):
                raise ExecutionError(
                    f"Index de liste hors limites: {index} (longueur: {len(collection)})",
                    node
                )
            
            return collection[index]
        
        elif isinstance(collection, dict):
            # Pour les dictionnaires : vérifier que la clé existe
            if index not in collection:
                raise ExecutionError(
                    f"Clé '{index}' introuvable dans le dictionnaire",
                    node
                )
            return collection[index]
        
        elif isinstance(collection, str):
            # Pour les chaînes : l'index doit être un entier
            if not isinstance(index, int):
                index_type = self._infer_type(index)
                raise ExecutionError(
                    f"Les indices de chaîne doivent être des entiers, pas '{index_type}'",
                    node
                )
            
            # Vérifier les bornes
            if index < 0:
                actual_index = len(collection) + index
                if actual_index < 0:
                    raise ExecutionError(
                        f"Index de chaîne hors limites: {index} (longueur: {len(collection)})",
                        node
                    )
                return collection[actual_index]
            elif index >= len(collection):
                raise ExecutionError(
                    f"Index de chaîne hors limites: {index} (longueur: {len(collection)})",
                    node
                )
            
            return collection[index]
        
        else:
            raise ExecutionError(
                f"Le type '{type(collection).__name__}' ne supporte pas l'indexation",
                node
            )
    
    # FIXME: changer type(obj).__name__ pour quelque chose qui reste au sein du langage
    # TODO: implémneter la possibilité de donner des attributes à des objets
    def visit_AttributeNode(self, node: AttributeNode) -> Any:
        obj = self.visit(node.object)
        
        try:
            return getattr(obj, node.attribute)
        except AttributeError:
            raise ExecutionError(
                f"L'objet de type '{type(obj).__name__}' n'a pas d'attribut '{node.attribute}'",
                node
            )
        
    # -------------------------------
    # Fonctions
        
    def visit_CallNode(self, node: CallNode) -> Any:
        # Résoudre la fonction
        if isinstance(node.function, str):
            try:
                func = self.current_env.lookup(node.function)
            except ExecutionError:
                raise ExecutionError(f"Fonction '{node.function}' non définie", node)
        else:
            func = self.visit(node.function)
        
        # Évaluer les arguments
        args = []
        kwargs = {}
        
        for arg_node in node.arguments:
            value = self.visit(arg_node.value)
            if arg_node.name is None:
                args.append(value)
            else:
                kwargs[arg_node.name] = value

        # Appeler la fonction
        try:
            if isinstance(func, BuiltinFunction):
                # Fonction built-in ou Python native
                return self._call_builtin_function(func, args, kwargs, node)
            elif isinstance(func, Function):
                # Fonction définie par l'utilisateur
                return self._call_user_function(func, args, kwargs, node)
            else:
                raise ExecutionError(f"'{func}' n'est pas appelable", node)
        except ReturnException as e:
            return e.value
        except (TypeError, ExecutionError) as e:
            raise ExecutionError(f"Erreur d'appel de fonction: {e}", node)
    
    def _call_builtin_function(self, func: BuiltinFunction, args: list, kwargs: dict, node: ASTNode) -> Any:
        """Appelle une fonction built-in"""
        return func(*args, **kwargs)
        # TODO : ExecutionError: Erreur à la ligne 16, colonne 6: Erreur d'appel de fonction: BuiltinMixin._setup_builtins.<locals>.builtin_print() got an unexpected keyword argument 'sep'
        #         Faire des vérifications sur les arguments pour avoir des erreurs non-python/personnalisées

    def _call_user_function(self, func: Function, args: list, kwargs: dict, node: ASTNode) -> Any:
        """Appelle une fonction définie par l'utilisateur"""
        # Créer un nouvel environnement pour la fonction
        func_env = Environment(parent=func.closure)
        
        # Lier les paramètres
        positional_params = []
        default_params = {}
        
        for param in func.parameters:
            if param.default_value is None:
                positional_params.append(param.name)
            else:
                default_params[param.name] = param.default_value
        
        # Assigner les arguments positionnels
        if len(args) > len(func.parameters):
            raise ExecutionError(
                f"Trop d'arguments pour '{func.name}': attendu {len(func.parameters)}, reçu {len(args)}",
                node
            )
        
        for i, arg_value in enumerate(args):
            param_name = func.parameters[i].name
            func_env.define(param_name, arg_value)
        
        # Assigner les arguments nommés et valeurs par défaut
        for param in func.parameters[len(args):]:
            if param.name in kwargs:
                func_env.define(param.name, kwargs[param.name])
            elif param.default_value is not None:
                # Évaluer la valeur par défaut dans l'environnement de la fonction
                old_env = self.current_env
                self.current_env = func_env
                default_val = self.visit(param.default_value)
                self.current_env = old_env
                func_env.define(param.name, default_val)
            else:
                raise ExecutionError(
                    f"Argument manquant pour le paramètre '{param.name}' de '{func.name}'",
                    node
                )
        
        # Exécuter le corps de la fonction
        old_env = self.current_env
        self.current_env = func_env
        
        try:
            result = None
            for statement in func.body:
                result = self.visit(statement)
            return result
        except ReturnException as e:
            return e.value
        finally:
            self.current_env = old_env
    
    # -------------------------------
    # Fonctions

    def visit_FunctionDefNode(self, node: FunctionDefNode) -> None:
        """Définit une fonction"""
        func = Function(node.name, node.parameters, node.body, self.current_env, node.return_type)
        self.current_env.define(node.name, func)
        return None

    def visit_ReturnNode(self, node: ReturnNode) -> None:
        """Gère l'instruction return"""
        value = self.visit(node.value) if node.value else None
        raise ReturnException(value)
