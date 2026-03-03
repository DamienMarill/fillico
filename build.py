#!/usr/bin/env python3
"""
🍭 Fillico - Build Script
Script pour générer les exécutables et installateurs
"""

import subprocess
import shutil
import sys
import os
from pathlib import Path

# Fix Windows encoding issues (emojis in print statements)
if sys.platform == "win32" and sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.platform == "win32" and sys.stderr is not None and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def clean_build():
    """Nettoie les dossiers de build précédents."""
    print("🧹 Nettoyage des builds précédents...")

    dirs_to_remove = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   Supprimé: {dir_name}/")


def build_exe():
    """Génère l'exécutable avec PyInstaller."""
    print("🔨 Génération de l'exécutable...")

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "PyInstaller",
                "fillico.spec",
                "--clean",
            ],
            check=True,
        )
        print("✅ Exécutable généré dans dist/Fillico.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la génération: {e}")
        return False


def run_tests():
    """Exécute les tests unitaires."""
    print("🧪 Exécution des tests...")

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "-v",
                "--tb=short",
            ],
            check=True,
        )
        print("✅ Tous les tests sont passés!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Certains tests ont échoué")
        return False


def main():
    """Point d'entrée du script de build."""
    import argparse

    parser = argparse.ArgumentParser(
        description="🍭 Fillico - Script de build"
    )
    parser.add_argument(
        "action",
        choices=["build", "test", "clean", "all"],
        help="Action à effectuer",
    )
    args = parser.parse_args()

    if args.action == "clean":
        clean_build()
    elif args.action == "test":
        run_tests()
    elif args.action == "build":
        build_exe()
    elif args.action == "all":
        clean_build()
        if run_tests():
            build_exe()
        else:
            print("❌ Build annulé à cause des tests échoués")
            sys.exit(1)


if __name__ == "__main__":
    main()
