<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Pylpex Banner</title>
    <style>
        body {
            font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 40px;
        }
        .banner {
            background: #faf9f9;
            padding: 40px 20px;
            border-radius: 12px;
            box-shadow: 0px 6px 18px rgba(255, 249, 249, 0.4);
            max-width: 900px;
            width: 100%;
            text-align: center;
        }
        .banner h1 {
            margin: 0;
            font-size: 3rem;
            line-height: 1.05;
            letter-spacing: -0.02em;
            color: #0f172a;
        }
        .banner .version {
            margin-top: 8px;
            font-size: 1rem;
            color: #475569;
        }
        .badges {
            margin-top: 14px;
            display: flex;
            justify-content: center;
            gap: 12px;
            align-items: center;
            flex-wrap: wrap;
        }
        .badges img {
            height: 22px;
        }
        .badges a {
            text-decoration: none;
            color: #0ea5a4;
            font-weight: 600;
            font-size: 0.9rem;
        }
        .banner p {
            margin: 18px auto 0;
            color: #64748b;
            max-width: 70%;
        }
    </style>
</head>
<body>
    <div class="banner">
        <h1>🌀 Pylpex</h1>
        <div class="version">Version <strong>1.0.0</strong></div>
        <div class="badges">
            <img src="https://img.shields.io/badge/Python-3.13+-blue.svg" alt="Python Version">
            <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
            <a href="https://github.com/votre-username/pylpex">GitHub /pylpex</a>
        </div>
        <p>Langage de programmation expérimental inspiré de Python.</p>
    </div>
    <br>
</body>
</html>

# Contexte

> Pylpex est un langage de programmation expérimental conçu comme un langage "jouet" pour explorer la conception d'un interpréteur de code.
Il reprend la simplicité syntaxique de Python, tout en introduisant une approche à base d’accolades {} pour structurer le code — à la manière du C ou du JavaScript et en remplacement de l’indentation de Python.

Le projet à une visée pédagogique et ne cherche pas à une utilisation concrète. Il comprend les étapes clés de la création d’un langage de programmation :

- la construction d’un lexer et d’un parser,

- la représentation d’un arbre syntaxique (AST),

- la gestion d’un environnement d’exécution,

- et la conception d’un moteur d’interprétation complet.

## 📚 Table des matières

* [Caractéristiques principales](#-caractéristiques-principales)
* [Installation](#-installation)
* [Utilisation](#-utilisation)
* [Syntaxe et concepts](#-syntaxe-et-concepts)
* [Exemples de code](#-exemples-de-code)
* [Architecture du projet](#-architecture-du-projet)
* [Licence et auteur](#-licence-et-auteur)

---

## ✨ Caractéristiques principales

Pylpex supporte déjà la majorité des constructions d’un langage moderne :

* **Types natifs** : entiers, flottants, booléens, chaînes, listes, dictionnaires, `none`
* **Structures de contrôle** : `if`, `else`, `for`, `while`, `break`, `continue`
* **Fonctions** avec paramètres par défaut, variables locales, et portée lexicale
* **Expressions ternaires** : `x if cond else y`
* **Opérateurs composés** (`+=`, `-=`, etc.)
* **Appels de fonction** comme objets de première classe

---

## 🚀 Installation

### Prérequis

* **Python 3.13+** (recommandé)
* [**uv**](https://docs.astral.sh/uv/) – un gestionnaire rapide pour Python, compatible avec `pyproject.toml`.

### Cloner le dépôt

```bash
git clone https://github.com/Golto/pylpex.git
cd pylpex
```

### Créer l’environnement et installer les dépendances

Si vous n’avez pas encore installé **uv** :

```bash
pip install uv
```

Ensuite, dans le dossier du projet :

```bash
uv sync
```

Cela crée un environnement virtuel local et installe automatiquement les dépendances définies dans `pyproject.toml`.

### Lancer le projet

```bash
uv run python main.py
```

---

💡 **Astuce :**
Vous pouvez aussi activer l’environnement virtuel avant de lancer des commandes :

```bash
source .venv/bin/activate  # sur Linux/macOS
# ou
.venv\Scripts\activate     # sur Windows
```

---

## 💻 Utilisation

Pylpex peut s’utiliser de deux manières :

1. **Depuis la console interactive** (REPL)
2. **Depuis un script Python**, en important l’interpréteur

---

### 🧠 1. Mode interactif (REPL)

```bash
python main.py
```

Vous verrez apparaître :

```
🌀 Pylpex 1.0.0
Langage expérimental inspiré de Python
Tapez 'exit' pour quitter.
>>> 
```

### Exemple rapide

```js
2 + sqrt(2)
```

Sortie :

```
3.414213562373095
```

> Ce mode permet de tester rapidement du code Pylpex sans créer de fichier.

---

### 🧩 2. Intégration dans du code Python

Pylpex peut être utilisé comme **librairie Python**.
Il expose une API simple pour **tokeniser**, **parser** et **évaluer** du code Pylpex :

```python
from src import Interpreter

# Crée un interpréteur avec environnement persistant
interpreter = Interpreter()

code = """
function add(a, b) {
    return a + b
}
print(add(5, 3))
"""

result = interpreter.evaluate(code)
```

#### Évaluer une expression simple

```python
from src.utils import evaluate

result = evaluate("2 + 2")
print(result)  # 4
```

#### Parser ou tokenizer seulement

```python
from src.utils import parse, tokenize

ast = parse("x = 5")
tokens = tokenize("x = 5")

print(ast)
print(tokens)
```

#### Conserver l’état entre plusieurs exécutions

```python
from src import Interpreter

interpreter = Interpreter()
interpreter.evaluate("x = 10")
interpreter.evaluate("y = x + 5")

print(interpreter.get_variable("y"))  # 15
```

#### Exécuter un fichier

```python
from src import Interpreter

interpreter = Interpreter()

with open("mon_script.txt", "r") as f:
    code = f.read()

result = interpreter.eval(code)
```

---

## 📖 Syntaxe et concepts

### Variables et types

```js
x = 10
name = "Alice"
values = [1, 2, 3]
```

### Conditions et boucles

```js
// Condition
if x > 5 {
    print("Grand")
} else {
    print("Petit")
}

// Boucle for
for item in [1, 2, 3] {
    print(item)
}

// Boucle while
count = 0
while count < 3 {
    print(count)
    count += 1
}

```

### Fonctions

```js
function greet(name = "World") {
    print("Hello, " + name + "!")
}

greet()
greet("Alice")
```

> **Note** : Vous pouvez consulter la [documentation complète de la syntaxe](doc/syntax.md) pour plus de détails.

---

## 🧩 Exemples de code

### Fibonacci

```js
function fib(n) {
    if n <= 1 {
        return n
    }
    return fib(n-1) + fib(n-2)
}

fib(10)
```

### Factorielle

```js
function factorial(n) {
    if n <= 1 {
        return 1
    } else {
        return n * factorial(n-1)
    }
}

factorial(5)
```

---

## 🏗️ Architecture du projet

Le cœur de Pylpex repose sur quatre composants :

| Composant       | Rôle                                            |
| --------------- | ----------------------------------------------- |
| **Lexer**       | Découpe le code source en *tokens*              |
| **Parser**      | Transforme les tokens en arbre syntaxique (AST) |
| **Evaluator**   | Exécute l’AST                                   |
| **Interpreter** | Coordonne l’ensemble et conserve l’état         |

```
Code source
   ↓
[Lexer] → Tokens
   ↓
[Parser] → AST
   ↓
[Evaluator] → Résultat
```

---

## 👤 Auteur et licence

- **Auteur :** Guillaume Foucaud
- **Licence :** MIT
- **GitHub :** [@Golto](https://github.com/Golto)
