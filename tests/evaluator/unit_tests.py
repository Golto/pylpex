from typing import List, Optional, Tuple, Any

TESTS = {
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
        # TODO add more cases
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

    # "postfix": [
    #     ("some_list[2]", "indexing"),
    #     ("person.name", "attribute"),
    #     ("node.value.type", "chained_attribute"),
    # ],

    # "complex": [
    #     ("- human.friends[2].age", "unary+attr+index"),
    #     ("x = [1, 2, 3]; x[1]", 2),
    #     ("d = { 'a': 5 }; d['a']", 5),
    # ],
}

def get_test_categories() -> List[str]:
    return list(TESTS.keys())


def get_test_cases(category: Optional[str] = None) -> Optional[List[Tuple[str, Any]]]:
    if category:
        return TESTS.get(category)
    return TESTS


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
