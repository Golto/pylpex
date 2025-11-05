
from typing import List, Optional, Callable
from functools import wraps
from pylpex.typesystem import TypeInfo, BaseType
from .exception import ExecutionError

class BuiltinFunction:
    """Représente une fonction builtin (native) avec typage statique connu."""
    def __init__(
        self,
        name: str,
        func: callable,
        arg_types: Optional[List[TypeInfo]] = None,
        return_type: Optional[TypeInfo] = None
    ):
        self.name = name
        self.func = func
        self.arg_types = arg_types or []
        self.return_type = return_type or TypeInfo(BaseType.ANY)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
    
    def __repr__(self) -> str:
        return f"<builtin-function {self.name}>"


# Décorateur pour définir facilement des builtins
def builtin(
    name: str = None,
    arg_types: List[TypeInfo] = None,
    return_type: TypeInfo = None
):
    """Décorateur pour enregistrer automatiquement une fonction builtin."""
    def decorator(func: Callable) -> BuiltinFunction:
        builtin_name = name or func.__name__.replace('_builtin_', '')
        
        # Marquer la fonction pour binding ultérieur
        func._builtin_meta = {
            'name': builtin_name,
            'arg_types': arg_types,
            'return_type': return_type
        }
        return func
    return decorator


class BuiltinMixin:

    def _setup_builtins(self):
        """Enregistre automatiquement toutes les fonctions built-in."""
        
        # Collecte automatique de toutes les fonctions décorées avec @builtin
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            
            # Vérifier si c'est une méthode avec métadonnées builtin
            if callable(attr) and hasattr(attr, '_builtin_meta'):
                meta = attr._builtin_meta

                # Créer un BuiltinFunction avec la méthode déjà bindée à self
                builtin_func = BuiltinFunction(
                    name=meta['name'],
                    func=attr,  # attr est déjà une méthode bindée (self est capturé)
                    arg_types=meta['arg_types'],
                    return_type=meta['return_type']
                )
                
                self.global_env.define(meta['name'], builtin_func)

    # =========================================================================
    # Type introspection
    # =========================================================================
    
    @builtin(
        name="get_type",
        arg_types=[TypeInfo(BaseType.ANY)],
        return_type=TypeInfo(BaseType.STRING)
    )
    def _builtin_get_type(self, x):
        return str(self._infer_type(x))
    
    @builtin(
        name="is_type",
        arg_types=[TypeInfo(BaseType.ANY), TypeInfo(BaseType.STRING)],
        return_type=TypeInfo(BaseType.BOOLEAN)
    )
    def _builtin_is_type(self, x, type_name):
        # TODO handle union types (eg. is_type(5, union[int, float]))
        # idée : reconstruire le type à partir de type_name et vérifier avec __eq__ sur TypeInfo
        return self._infer_type(x).base.value == type_name
    
    @builtin(
        name="convert_to",
        arg_types=[TypeInfo(BaseType.ANY), TypeInfo(BaseType.STRING)],
        return_type=TypeInfo(BaseType.ANY)
    )
    def _builtin_convert_to(self, x, type_name):
        # TODO handler more types
        if type_name == "int":
            return int(x)
        elif type_name == "float":
            return float(x)
        elif type_name == "string":
            return str(x)
        elif type_name == "boolean":
            return bool(x)
        raise ExecutionError(f"Conversion de type non supportée vers {type_name}")

    # =========================================================================
    # I/O
    # =========================================================================
    
    @builtin(
        name="print",
        arg_types=[TypeInfo(BaseType.VARIADIC, subtypes=[TypeInfo(BaseType.ANY)])],
        return_type=TypeInfo(BaseType.NONE)
    )
    def _builtin_print(self, *args):
        print(*args)
        return None

    # =========================================================================
    # Math
    # =========================================================================
    
    @builtin(
        name="sqrt",
        arg_types=[TypeInfo(BaseType.FLOAT)],
        return_type=TypeInfo(BaseType.FLOAT)
    )
    def _builtin_sqrt(self, x):
        import math
        return math.sqrt(float(x))
    
    @builtin(
        name="abs",
        arg_types=[TypeInfo(BaseType.FLOAT)],
        return_type=TypeInfo(BaseType.FLOAT)
    )
    def _builtin_abs(self, x):
        return abs(x)
    
    @builtin(
        name="min",
        arg_types=[TypeInfo(BaseType.VARIADIC, subtypes=[TypeInfo(BaseType.FLOAT)])],
        return_type=TypeInfo(BaseType.FLOAT)
    )
    def _builtin_min(self, *args):
        if not args:
            raise ExecutionError("min() nécessite au moins un argument")
        return min(args)
    
    @builtin(
        name="max",
        arg_types=[TypeInfo(BaseType.VARIADIC, subtypes=[TypeInfo(BaseType.FLOAT)])],
        return_type=TypeInfo(BaseType.FLOAT)
    )
    def _builtin_max(self, *args):
        if not args:
            raise ExecutionError("max() nécessite au moins un argument")
        return max(args)

    # =========================================================================
    # String
    # =========================================================================
    
    @builtin(
        name="capitalize",
        arg_types=[TypeInfo(BaseType.STRING)],
        return_type=TypeInfo(BaseType.STRING)
    )
    def _builtin_capitalize(self, s):
        return s.capitalize()
    
    @builtin(
        name="lower",
        arg_types=[TypeInfo(BaseType.STRING)],
        return_type=TypeInfo(BaseType.STRING)
    )
    def _builtin_lower(self, s):
        return s.lower()
    
    @builtin(
        name="upper",
        arg_types=[TypeInfo(BaseType.STRING)],
        return_type=TypeInfo(BaseType.STRING)
    )
    def _builtin_upper(self, s):
        return s.upper()
    
    @builtin(
        name="split",
        arg_types=[TypeInfo(BaseType.STRING), TypeInfo(BaseType.STRING)],
        return_type=TypeInfo(BaseType.LIST, subtypes=[TypeInfo(BaseType.STRING)])
    )
    def _builtin_split(self, s, delimiter):
        return s.split(delimiter)
    
    @builtin(
        name="join",
        arg_types=[TypeInfo(BaseType.STRING), TypeInfo(BaseType.LIST)],
        return_type=TypeInfo(BaseType.STRING)
    )
    def _builtin_join(self, lst, separator):
        return separator.join(str(x) for x in lst)

    # =========================================================================
    # List
    # =========================================================================
    
    @builtin(
        name="len",
        arg_types=[TypeInfo(BaseType.LIST)],
        return_type=TypeInfo(BaseType.INTEGER)
    )
    def _builtin_len(self, x):
        if isinstance(x, (str, list)):
            return len(x)
        raise ExecutionError(f"len() s'attend à un argument de type string ou list, a reçu {self._infer_type(x)}")
    
    @builtin(
        name="append",
        arg_types=[TypeInfo(BaseType.LIST), TypeInfo(BaseType.ANY)],
        return_type=TypeInfo(BaseType.NONE)
    )
    def _builtin_append(self, lst, x):
        lst.append(x)
        return None
    
    @builtin(
        name="pop",
        arg_types=[TypeInfo(BaseType.LIST)],
        return_type=TypeInfo(BaseType.ANY)
    )
    def _builtin_pop(self, lst):
        return lst.pop()
    
    @builtin(
        name="copy",
        arg_types=[TypeInfo(BaseType.LIST)],
        return_type=TypeInfo(BaseType.LIST)
    )
    def _builtin_copy(self, lst):
        return lst.copy()
    
    @builtin(
        name="reverse",
        arg_types=[TypeInfo(BaseType.LIST)],
        return_type=TypeInfo(BaseType.NONE)
    )
    def _builtin_reverse(self, lst):
        lst.reverse()
        return None
    
    @builtin(
        name="sort",
        arg_types=[TypeInfo(BaseType.LIST)],
        return_type=TypeInfo(BaseType.NONE)
    )
    def _builtin_sort(self, lst):
        lst.sort()
        return None
    
    @builtin(
        name="range",
        arg_types=[TypeInfo(BaseType.INTEGER), TypeInfo(BaseType.INTEGER)],
        return_type=TypeInfo(BaseType.LIST, subtypes=[TypeInfo(BaseType.INTEGER)])
    )
    def _builtin_range(self, start, end):
        if not isinstance(start, int) or not isinstance(end, int):
            raise ExecutionError("range() attend deux entiers")
        return list(range(start, end + 1))
