from typing import List, Optional, Tuple, Any

TESTS = {
    "comments": [
        ("// comment", None),
        ("/* comment */", None),
        ("/* multi\nline\ncomment */", None),
    ],

    "literals": [
        ("none", None),
        ("45", 45),
        ("4.5", 4.5),
        ("'hello world'", "hello world"),
        ("true", True),
        ("false", False),
        ("[4, 5, 6]", [4, 5, 6]),
        ("{ 'a': 1, 'b': 2, 'c': 3 }", {"a": 1, "b": 2, "c": 3}),
    ],

    "indexing": [
        ("[1, 2, 3][1]", 2),
        ("{ 'a': 1, 'b': 2, 'c': 3 }['b']", 2),
        ("name = 'John'; name[1]", "o"),
        # errors list indexing
        ("array = [1, 2, 3, 4, 5]; array[1.2]", "Error: Les indices de liste doivent être des entiers"),
        ("array = [1, 2, 3, 4, 5]; array[15]", "Error: Index de liste hors limites"),
        ("array = [1, 2, 3, 4, 5]; array[-1]", 5),
        ("array = [1, 2, 3, 4, 5]; array[-6]", "Error: Index de liste hors limites"),
        # errors dict indexing
        ("mapping = { 'a': 1, 'b': 2, 'c': 3 }; mapping['d']", "Error: Clé 'd' introuvable dans le dictionnaire"),
        # errors string indexing
        ("name = 'John'; name[1.2]", "Error: Les indices de chaîne doivent être des entiers"),
        ("name = 'John'; name[10]", "Error: Index de chaîne hors limites"),
        ("name = 'John'; name[-1]", "n"),
        ("name = 'John'; name[-5]", "Error: Index de chaîne hors limites"),
        # no support
        ("x = 1245; x[1]", "Error: ne supporte pas l'indexation"),
    ],

    "assignments": [
        ("x", "Error: Variable 'x' non définie"),
        ("x = 5; x", 5),
        ("y = 'ok'; y", "ok"),
        ("z = true; z", True),
        ("x = 5; x = 6; x", 6),
        ("x = 5; x += 6; x", 11),
        ("x = 5; x -= 6; x", -1),
        ("x = 5; x *= 6; x", 30),
        ("x = 5; x /= 6; x", 5/6),
        ("x = 5; x **= 6; x", 5**6),
        ("x = 12; x %= 5; x", 12 % 5),
        ("x = 5; y = 7; x += y; [x, y]", [12, 7]),
    ],

    "assignments_indexing": [
        ("x = [1, 2, 3]; x[1] = 5; x", [1, 5, 3]),
        ("x = [1, 2, 3]; x[1] += 5; x", [1, 7, 3]),
        ("x = [1, 2, 3]; x[1] -= 5; x", [1, -3, 3]),
        ("x = [1, 2, 3]; x[1] *= 5; x", [1, 10, 3]),
        ("x = [1, 2, 3]; x[1] /= 5; x", [1, 0.4, 3]),
        ("x = [1, 2, 3]; x[1] **= 5; x", [1, 32, 3]),
        ("x = [1, 2, 3]; x[2] %= 2; x", [1, 2, 1]),
    ],

    "binary_ops": [
        ("true or false", True or False),
        ("true and false", True and False),
        ("3 + 5", 3 + 5),
        ("8 - 3", 8 - 3),
        ("4 * 3", 4 * 3),
        ("4 / 5", 4 / 5),
        ("3 ** 2", 3 ** 2),
        ("12 % 5", 12 % 5),
        ("1 / 0", "Error: Division par zéro"),
        ("35 == 36", 35 == 36),
        ("35 != 36", 35 != 36),
        ("35 < 36", 35 < 36),
        ("35 <= 36", 35 <= 36),
        ("35 > 36", 35 > 36),
        ("35 >= 36", 35 >= 36),
        ("3 in [1, 2, 3]", 3 in [1, 2, 3]),
        ("4 in [1, 2, 3]", 4 in [1, 2, 3]),
        ("'a' in {'a': 1, 'b': 2}", 'a' in {'a': 1, 'b': 2}),
        ("'c' in {'a': 1, 'b': 2}", 'c' in {'a': 1, 'b': 2}),
        ("89 + 3 * (4 + 5) - 2 ** (7 - 5) * (4 + 7)", 72)
    ],

    "unary_ops": [
        ("-7", -7),
        ("+4.5", +4.5),
        ("not true", not True),
    ],
    
    "ternary": [
        ('"ok" if true else "no"', "ok"), 
    ],

    "control_flow": [
        ("if true {'Vrai'}", "Vrai"),
        ("if true {'Vrai'} else {'Faux'}", "Vrai"),
        ("if false {'Vrai'} else {'Faux'}", "Faux"),
        ("count = 0; while count < 10 { count += 1 } count", 10),
        ("count = 0; while count < 10 { count += 1; if count == 5 { break } } count", 5),
        ("count = 0; while count < 10 { count += 1; if count == 5 { count+= 10; continue } } count", 15),
        ("sum = 0; for i in [1, 2, 3, 4, 5] { sum += i } sum", 15),
        ("sum = 0; for i in [1, 2, 3, 4, 5] { sum += i; if i == 3 { break }} sum", 6),
        ("sum = 0; for i in [1, 2, 3, 4, 5] { if i == 3 { continue } sum += i } sum", 12),
    ],

    "functions": [
        ("def add(a, b) { return a + b } add(1, 2)", 3),
        ("def add(a, b, c = 0) { return a + b + c } add(1, 2)", 3),
        ("def add(a, b, c = 0) { return a + b + c } add(1, 2, 3)", 6),
        ("def add(a, b) { return a + b } add_ = add; add_(1, 2)", 3),
        ("def add(a, b) { return a + b } array = [add]; array[0](1, 2)", 3),
        ("some_function = 78; some_function()", "Error: n'est pas appelable"),
        ("sqrt(2)", 1.4142135623730951),
    ]
}

def get_test_categories() -> List[str]:
    return list(TESTS.keys())


def get_test_cases(category: Optional[str] = None) -> Optional[List[Tuple[str, Any]]]:
    if category:
        return TESTS.get(category)
    return [test for tests in TESTS.values() for test in tests]


def run_tests(tests):
    from src.utils import evaluate
    for expr, expected in tests:
        print("------------------------------------------------")
        print(expr)
        try:
            result = evaluate(expr)
            print("\tResult:   ", result)
            print("\tExpected: ", expected)
            if isinstance(expected, str) and expected.startswith("Error:"):
                print("\tCorrect:  🟥 (aucune erreur levée)")
            else:
                print("\tCorrect:  ✅" if result == expected else "🟥")
        except Exception as e:
            error_message = str(e)
            print("\tError:    ", error_message)
            print("\tExpected: ", expected)
            if isinstance(expected, str) and expected.startswith("Error:"):
                expected_error_msg = expected.split("Error:")[1].strip()
                print("\tCorrect:  ✅" if expected_error_msg in error_message else "🟥")
            else:
                print("\tCorrect:  🟥 (erreur inattendue)")
