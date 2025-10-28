import sys
from src.pylpex import Interpreter, __version__, __author__, __email__

# -----------------------------------------------------
# Métadonnées du langage
LANGUAGE_NAME = "Pylpex"
LANGUAGE_VERSION = __version__
AUTHOR = __author__
EMAIL = __email__
DESCRIPTION = (
    "Langage de programmation 'jouet' inspiré de Python, "
    "mais avec des différences syntaxiques (ex: blocs avec {} au lieu des indentations)."
)

# -----------------------------------------------------
# Fonctions utilitaires d'affichage

def color(text, code):
    """Couleurs simples ANSI (si terminal compatible)."""
    if sys.stdout.isatty():
        return f"\033[{code}m{text}\033[0m"
    return text

def green(text): return color(text, "92")
def red(text): return color(text, "91")
def cyan(text): return color(text, "96")
def yellow(text): return color(text, "93")
def bold(text): return color(text, "1")

# -----------------------------------------------------
# Message de bienvenue

def banner():
    print()
    print(bold(f"🌀 {LANGUAGE_NAME} {LANGUAGE_VERSION}"))
    print(cyan(DESCRIPTION))
    print(f"Auteur : {AUTHOR}  •  Contact : {EMAIL}")
    print("Tapez 'exit' ou Ctrl+C pour quitter.\n")

# -----------------------------------------------------
# Boucle principale (REPL)

def main():
    interpreter = Interpreter()
    banner()

    while True:
        try:
            code = input(bold(">>> "))
            if not code.strip():
                continue

            if code.strip().lower() in {"exit", "quit"}:
                print("Programme quitté.")
                break

            result = interpreter.evaluate(code)
            if result is not None:
                print(green("<"), result)

        except KeyboardInterrupt:
            print("\nInterruption. Tapez 'exit' pour quitter.")
        except EOFError:
            print("\nFin de fichier.")
            break
        except Exception as e:
            print(red(f"Erreur: {e}"))
    print()

# -----------------------------------------------------
# Entrée principale

if __name__ == "__main__":
    main()
