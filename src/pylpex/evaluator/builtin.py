
from typing import List, Optional
from pylpex.typesystem import TypeInfo, BaseType

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
    

class BuiltinMixin:

    def _setup_builtins(self):
        """Définit les fonctions built-in"""
        # from .builtin import builtin_get_type, builtin_print, builtin_sqrt
        
        def builtin_get_type(x):
            return str(self._infer_type(x))

        def builtin_print(*args):
            print(*args)
            return None

        def builtin_sqrt(x: float) -> float:
            import math
            return math.sqrt(x)

        # Enregistrement des builtins
        self.global_env.define("get_type", BuiltinFunction(
            name="get_type",
            func=builtin_get_type,
            arg_types=[TypeInfo(BaseType.ANY)],
            return_type=TypeInfo(BaseType.STRING)
        ))

        self.global_env.define("print", BuiltinFunction(
            name="print",
            func=builtin_print,
            arg_types=[TypeInfo(BaseType.VARIADIC, subtypes=[TypeInfo(BaseType.ANY)])],
            return_type=TypeInfo(BaseType.NONE)
        ))

        self.global_env.define("sqrt", BuiltinFunction(
            name="sqrt",
            func=builtin_sqrt,
            arg_types=[TypeInfo(BaseType.FLOAT)],
            return_type=TypeInfo(BaseType.FLOAT)
        ))