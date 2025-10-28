
from typing import Optional
from pylpex.parser.ASTNodes import *
from .environment import Environment, RuntimeErrorEx
from .visitor import ASTVisitor


class BreakException(Exception):
    """Exception pour gérer l'instruction break"""
    pass


class ContinueException(Exception):
    """Exception pour gérer l'instruction continue"""
    pass


class ReturnException(Exception):
    """Exception pour gérer l'instruction return"""
    def __init__(self, value):
        self.value = value


class Function:
    """Représente une fonction définie par l'utilisateur"""
    def __init__(self, name: str, parameters: List[ParameterNode], body: List[ASTNode], closure: Environment):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.closure = closure
    
    def __repr__(self):
        return f"<function {self.name}>"
    

class Evaluator(ASTVisitor):
    """Évalue l'AST dans un environnement donné"""

    def __init__(self, global_env: Optional[Environment] = None):
        self.global_env = global_env or Environment()
        self.current_env = self.global_env
        self._setup_builtins()

    def _setup_builtins(self):
        """Définit les fonctions built-in"""

        def builtin_print(*args):
            print(*args)
            return None
        
        def builtin_sqrt(x: float) -> float:
            import math
            return math.sqrt(x)
        
        # Enregistrement des builtins
        self.global_env.define("print", builtin_print)
        self.global_env.define("sqrt", builtin_sqrt)

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
                    raise RuntimeErrorEx("Division par zéro", node)
                return current / value
            elif operator == AssignmentOperatorType.POWER:
                return current ** value
            elif operator == AssignmentOperatorType.MOD:
                return current % value
            else:
                raise RuntimeErrorEx(f"Opérateur composé inconnu: {operator}", node)
        except Exception as e:
            raise RuntimeErrorEx(f"Erreur d'opération: {e}", node)
        
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
                except RuntimeErrorEx:
                    raise RuntimeErrorEx(f"Variable '{node.target.name}' non définie", node)
                
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
                    raise RuntimeErrorEx(f"Erreur d'assignation: {e}", node)
            else:
                # Opérateurs composés
                try:
                    current = collection[index]
                except (TypeError, KeyError, IndexError) as e:
                    raise RuntimeErrorEx(f"Erreur de lecture: {e}", node)
                
                value = self._apply_compound_operator(node.operator, current, value, node)
                
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
        
        # Vérifications selon le type de collection
        if isinstance(collection, list):
            # Pour les listes : l'index doit être un entier
            if not isinstance(index, int):
                # FIXME Ne pas utiliser type(index).__name__ (c'est du type Python =( )
                raise RuntimeErrorEx(
                    f"Les indices de liste doivent être des entiers, pas '{type(index).__name__}'",
                    node
                )
            
            # Vérifier les bornes
            if index < 0:
                # Support des indices négatifs comme en Python
                actual_index = len(collection) + index
                if actual_index < 0:
                    raise RuntimeErrorEx(
                        f"Index de liste hors limites: {index} (longueur: {len(collection)})",
                        node
                    )
                return collection[actual_index]
            elif index >= len(collection):
                raise RuntimeErrorEx(
                    f"Index de liste hors limites: {index} (longueur: {len(collection)})",
                    node
                )
            
            return collection[index]
        
        elif isinstance(collection, dict):
            # Pour les dictionnaires : vérifier que la clé existe
            if index not in collection:
                raise RuntimeErrorEx(
                    f"Clé '{index}' introuvable dans le dictionnaire",
                    node
                )
            return collection[index]
        
        elif isinstance(collection, str):
            # Pour les chaînes : l'index doit être un entier
            if not isinstance(index, int):
                raise RuntimeErrorEx(
                    f"Les indices de chaîne doivent être des entiers, pas '{type(index).__name__}'",
                    node
                )
            
            # Vérifier les bornes
            if index < 0:
                actual_index = len(collection) + index
                if actual_index < 0:
                    raise RuntimeErrorEx(
                        f"Index de chaîne hors limites: {index} (longueur: {len(collection)})",
                        node
                    )
                return collection[actual_index]
            elif index >= len(collection):
                raise RuntimeErrorEx(
                    f"Index de chaîne hors limites: {index} (longueur: {len(collection)})",
                    node
                )
            
            return collection[index]
        
        else:
            raise RuntimeErrorEx(
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
            raise RuntimeErrorEx(
                f"L'objet de type '{type(obj).__name__}' n'a pas d'attribut '{node.attribute}'",
                node
            )
        
    def visit_CallNode(self, node: CallNode) -> Any:
        # Résoudre la fonction
        if isinstance(node.function, str):
            try:
                func = self.current_env.lookup(node.function)
            except RuntimeErrorEx:
                raise RuntimeErrorEx(f"Fonction '{node.function}' non définie", node)
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
            if callable(func) and not isinstance(func, Function):
                # Fonction built-in ou Python native
                return func(*args, **kwargs)
            elif isinstance(func, Function):
                # Fonction définie par l'utilisateur
                return self._call_user_function(func, args, kwargs, node)
            else:
                raise RuntimeErrorEx(f"'{func}' n'est pas appelable", node)
        except ReturnException as e:
            return e.value
        except (TypeError, RuntimeErrorEx) as e:
            raise RuntimeErrorEx(f"Erreur d'appel de fonction: {e}", node)
    
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
            raise RuntimeErrorEx(
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
                raise RuntimeErrorEx(
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
    

    def visit_BreakNode(self, node: BreakNode) -> None:
        """Gère l'instruction break"""
        raise BreakException()
    

    def visit_ContinueNode(self, node: ContinueNode) -> None:
        """Gère l'instruction continue"""
        raise ContinueException()
    

    def visit_WhileNode(self, node: WhileNode) -> None:
        """Évalue une boucle while"""
        try:
            while self.visit(node.condition):
                try:
                    for statement in node.body:
                        self.visit(statement)
                except ContinueException:
                    continue
        except BreakException:
            pass
        
        return None
    
    
    def visit_ForNode(self, node: ForNode) -> None:
        """Évalue une boucle for"""
        iterable = self.visit(node.iterable)
        
        try:
            iter(iterable)
        except TypeError:
            raise RuntimeErrorEx(f"L'objet de type '{type(iterable).__name__}' n'est pas itérable", node)
        
        try:
            for value in iterable:
                self.current_env.define(node.variable, value)
                try:
                    for statement in node.body:
                        self.visit(statement)
                except ContinueException:
                    continue
        except BreakException:
            pass
        
        return None
    
    # -------------------------------
    # Fonctions

    def visit_FunctionDefNode(self, node: FunctionDefNode) -> None:
        """Définit une fonction"""
        func = Function(node.name, node.parameters, node.body, self.current_env)
        self.current_env.define(node.name, func)
        return None

    def visit_ReturnNode(self, node: ReturnNode) -> None:
        """Gère l'instruction return"""
        value = self.visit(node.value) if node.value else None
        raise ReturnException(value)
