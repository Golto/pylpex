from typing import List, Optional, Any
from src.lexer import Lexer, Token
from src.parser import Parser, ASTNode
from src.evaluator import Evaluator

class Interpreter:
    """
    Interpréteur principal qui coordonne le lexer, parser et evaluator.
    Peut être utilisé pour des exécutions multiples avec un état partagé.
    """
    
    def __init__(self, reset_on_error: bool = False):
        """
        Initialise l'interpréteur.
        
        Args:
            reset_on_error: Si True, réinitialise l'environnement en cas d'erreur
        """
        self.evaluator = Evaluator()
        self.reset_on_error = reset_on_error

    def tokenize(self, code: str) -> List[Token]:
        """
        Tokenize le code source.
        
        Args:
            code: Code source à analyser
            
        Returns:
            Liste de tokens
        """
        lexer = Lexer(code)
        return lexer.tokenize()
    
    def parse(self, code: str) -> ASTNode:
        """
        Parse le code source en AST.
        
        Args:
            code: Code source à parser
            
        Returns:
            Arbre syntaxique abstrait (AST)
        """
        tokens = self.tokenize(code)
        parser = Parser(tokens)
        return parser.parse()
    
    def evaluate(self, code: str) -> Any:
        """
        Évalue le code source et retourne le résultat.
        Conserve l'état entre les appels (variables, fonctions définies, etc.).
        
        Args:
            code: Code source à évaluer
            
        Returns:
            Résultat de l'évaluation
        """
        try:
            ast = self.parse(code)
            return self.evaluator.evaluate(ast)
        except Exception as e:
            if self.reset_on_error:
                self.reset()
            raise

    def eval_ast(self, ast: ASTNode) -> Any:
        """
        Évalue un AST déjà parsé.
        
        Args:
            ast: Arbre syntaxique à évaluer
            
        Returns:
            Résultat de l'évaluation
        """
        try:
            return self.evaluator.eval(ast)
        except Exception as e:
            if self.reset_on_error:
                self.reset()
            raise

    def reset(self):
        """Réinitialise l'environnement de l'interpréteur."""
        self.evaluator = Evaluator()

    # ----------------------------------------------------------
    # Gestion des variables et fonctions dans l'environnement
    
    def get_variable(self, name: str) -> Any:
        """
        Récupère la valeur d'une variable dans l'environnement global.
        
        Args:
            name: Nom de la variable
            
        Returns:
            Valeur de la variable
        """
        return self.evaluator.global_env.lookup(name)
    
    def set_variable(self, name: str, value: Any):
        """
        Définit une variable dans l'environnement global.
        
        Args:
            name: Nom de la variable
            value: Valeur à assigner
        """
        self.evaluator.global_env.define(name, value)
    
    def has_variable(self, name: str) -> bool:
        """
        Vérifie si une variable existe dans l'environnement.
        
        Args:
            name: Nom de la variable
            
        Returns:
            True si la variable existe
        """
        try:
            self.evaluator.global_env.lookup(name)
            return True
        except:
            return False