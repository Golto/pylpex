TESTS = [
    (
        "parse_primary",
        ["none", "5", "4.69", "'hello world'", "true", "false", "x"]
    ),
    (
        "parse_unary_or_primary",
        [
            "some_list[0]", "x[0][1]", "x[index]", # postfixes
            "not true", "-3", "+2.78", # unary operators
            "human.name", "node.value.type", # attributes
            "- human.friends[2].age", # mixed up
        ]
    ),
    (
        "parse_expression",
        [
            "5", " - (- 5)",
            "[1, 2, 3]", "['a', 'b', 'c']",
            "{'a': 1, 'b': 2}",
            "1 + 2", "47 - 58 * 6", "(47 - 58) * 6", "index + 7 * (4 + divisor / 5 % 7) ** 2",
            "78 > 47", "78 >= 47", "78 < 47", "78 <= 47", "78 == 47", "78 != 47", "78 == 47 and 47 < 78", "78 == 47 or 47 < 78",
            "42 if universe.question == 'The answer to life, the universe and everything' else none", # ternary
        ]
    ),
    (
        "parse_statement",
        [
            "x = 42",
            "position += velocity * dt",
            "position -= velocity * dt",
            "power *= 2",
            "power /= 2",
            "seed %= 17",
            "length **= 2",
        ]
    ),
    (
        "parse_parameter_list", 
        ["(a, b, c)", "(a, b, x = none)"]
    ),
    (
        "parse_function_def",
        [
            "function f(a) { }",
            "function f(a, b, c) { return a + b + c }",
            "function get_value(a) { x = a; return x }",
        ]
    ),
    (
        "parse_unary_or_primary", 
        [
            "get_value(42, name='John Doe')"
        ]
    ),
    (
        "parse_statement",
        [
            "if true { 45 }",
            "if true { 45 } else { 46 }",
            "if true 45",
            "while true { 45; 46 }",
            "x in [1, 2, 3]",
            "return", "return some_value",
            "for x in list { break }",
            "for x in list { continue }",
            "while cond { break }",
            "while cond { continue }",
        ]
    ),
]


def get_test_cases():
    return TESTS

def run_tests(tests):
    from src.lexer import Lexer
    from src.parser import Parser
    from src.utils import format_ast
    for parse_method, lines in tests:
        print(f"  Testing {parse_method.upper()}")
        print("=====================================")
        for code in lines:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            node = parser.__getattribute__(parse_method)()
            print("-------------------------------------")
            print(code)
            print(
                format_ast(node)
            )
        print()
        