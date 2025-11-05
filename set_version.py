#!/usr/bin/env python3
"""
set_version.py
---------------
Script utilitaire pour mettre à jour la version du projet dans plusieurs fichiers clés.

🔧 Fonctionnement :
    - Met à jour automatiquement la version dans :
        1. assets/banner.svg       → le texte visible sur la bannière (<tspan font-weight="600">x.x.x</tspan>)
        2. pyproject.toml          → la ligne 'version = "x.x.x"'
        3. src/pylpex/__init__.py  → la ligne '__version__ = "x.x.x"'

💻 Utilisation :
    python set_version.py -V <version>

    Exemple :
        python set_version.py -V 1.2.0

📋 Remarques :
    - Le format de version doit être de la forme x.y.z (ex: 1.0.3)
    - Le script vérifie l'existence de chaque fichier avant de le modifier.
"""

import sys
import re
from pathlib import Path

# --- Fichiers à modifier ---
FILES = [
    Path("assets/banner.svg"),
    Path("pyproject.toml"),
    Path("src/pylpex/__init__.py"),
]

def update_file(path: Path, version: str):
    """Met à jour la version dans un fichier donné."""
    if not path.exists():
        print(f"⚠️  Fichier introuvable : {path}")
        return

    text = path.read_text(encoding="utf-8")

    if path.suffix == ".svg":
        # Remplace la ligne contenant <tspan font-weight="600">x.x.x</tspan>
        text = re.sub(
            r"(<tspan font-weight=\"600\">)([\d.]+)(</tspan>)",
            rf"\g<1>{version}\g<3>",
            text
        )

    elif path.name == "pyproject.toml":
        # Remplace la ligne version = "x.x.x"
        text = re.sub(
            r'version\s*=\s*"[0-9.]+"',
            f'version = "{version}"',
            text
        )

    elif path.name == "__init__.py":
        # Remplace __version__ = "x.x.x"
        text = re.sub(
            r'__version__\s*=\s*"[0-9.]+"',
            f'__version__ = "{version}"',
            text
        )

    else:
        print(f"ℹ️  Aucun modèle de remplacement pour {path}")
        return

    path.write_text(text, encoding="utf-8")
    print(f"✅ Version mise à jour dans {path}")

def main():
    if len(sys.argv) != 3 or sys.argv[1] != "-V":
        print("Usage: python set_version.py -V <version>")
        sys.exit(1)

    version = sys.argv[2]
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        print("❌ Format de version invalide (attendu: x.y.z)")
        sys.exit(1)

    for f in FILES:
        update_file(f, version)

if __name__ == "__main__":
    main()
