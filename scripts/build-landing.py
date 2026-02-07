#!/usr/bin/env python3
"""
🍭 Fililico - Script de build de la landing page

Ce script prépare la landing page pour le déploiement sur GitHub Pages :
1. Copie les assets du projet vers le dossier landing
2. Génère les placeholders d'images si nécessaires
3. Optionnellement déploie vers la branche gh-pages

Usage:
    python scripts/build-landing.py           # Build seulement
    python scripts/build-landing.py --deploy  # Build et déploie
"""

import shutil
import subprocess
import sys
from pathlib import Path
from argparse import ArgumentParser


# Chemins
PROJECT_ROOT = Path(__file__).parent.parent
LANDING_DIR = PROJECT_ROOT / "landing"
WEB_ASSETS = PROJECT_ROOT / "web" / "assets"
LANDING_ASSETS = LANDING_DIR / "assets"


def log(emoji: str, message: str):
    """Affiche un message avec un emoji."""
    print(f"{emoji}  {message}")


def copy_assets():
    """Copie les assets du projet vers la landing page."""
    log("📂", "Copie des assets...")
    
    # Créer le dossier assets/images si nécessaire
    images_dir = LANDING_ASSETS / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Copier depuis web/assets
    if WEB_ASSETS.exists():
        for item in WEB_ASSETS.rglob("*"):
            if item.is_file():
                relative = item.relative_to(WEB_ASSETS)
                dest = LANDING_ASSETS / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
                log("  ✓", f"Copié: {relative}")
    
    # Vérifier les fichiers requis
    required_files = [
        "images/logo.png",
        "images/mascot.png",
    ]
    
    missing = []
    for f in required_files:
        if not (LANDING_ASSETS / f).exists():
            missing.append(f)
    
    if missing:
        log("⚠️", f"Fichiers manquants: {', '.join(missing)}")
        log("💡", "Créez ces fichiers ou utilisez des placeholders")
    else:
        log("✅", "Tous les assets requis sont présents")


def create_placeholders():
    """Crée des images placeholder si nécessaires."""
    from PIL import Image, ImageDraw, ImageFont
    
    images_dir = LANDING_ASSETS / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    placeholders = {
        "logo.png": (100, 100, "#F472B6", "🍭"),
        "mascot.png": (400, 400, "#FDF2F8", "( ≧◡≦ )"),
        "stamp_1.png": (100, 100, "#FDF2F8", "( • ᴗ • )"),
        "stamp_2.png": (100, 100, "#FDF2F8", "( ◕ 0 ◕ )"),
        "stamp_3.png": (100, 100, "#FDF2F8", "( >_< )"),
        "stamp_4.png": (100, 100, "#FDF2F8", "( ≧◡≦ )"),
    }
    
    for filename, (w, h, bg, text) in placeholders.items():
        filepath = images_dir / filename
        if not filepath.exists():
            log("🎨", f"Création du placeholder: {filename}")
            img = Image.new('RGBA', (w, h), bg)
            draw = ImageDraw.Draw(img)
            
            # Centrer le texte
            bbox = draw.textbbox((0, 0), text)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (w - text_w) // 2
            y = (h - text_h) // 2
            draw.text((x, y), text, fill="#4C1D95")
            
            img.save(filepath)


def deploy_to_gh_pages():
    """Déploie vers la branche gh-pages."""
    log("🚀", "Déploiement vers gh-pages...")
    
    import tempfile
    import os
    
    # Créer un dossier temporaire
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Copier la landing
        shutil.copytree(LANDING_DIR, tmpdir / "landing")
        
        # Aller dans le repo
        os.chdir(PROJECT_ROOT)
        
        # Créer/switch vers gh-pages
        result = subprocess.run(
            ["git", "checkout", "--orphan", "gh-pages"],
            capture_output=True
        )
        
        if result.returncode != 0:
            # La branche existe déjà
            subprocess.run(["git", "checkout", "gh-pages"], check=True)
        
        # Supprimer tout sauf .git
        for item in PROJECT_ROOT.iterdir():
            if item.name != ".git":
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        
        # Copier les fichiers de la landing
        for item in (tmpdir / "landing").iterdir():
            if item.is_dir():
                shutil.copytree(item, PROJECT_ROOT / item.name)
            else:
                shutil.copy2(item, PROJECT_ROOT / item.name)
        
        # Créer .nojekyll
        (PROJECT_ROOT / ".nojekyll").touch()
        
        # Commit et push
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run([
            "git", "commit", "-m", 
            "🚀 Deploy landing page\n\nCo-Authored-By: Meika <meika@marill.dev>"
        ], check=True)
        subprocess.run(["git", "push", "-f", "origin", "gh-pages"], check=True)
        
        # Retourner à main/master
        subprocess.run(["git", "checkout", "-"], check=True)
    
    log("✅", "Déploiement terminé !")


def main():
    parser = ArgumentParser(description="Build de la landing page Fililico")
    parser.add_argument("--deploy", action="store_true", help="Déployer vers gh-pages")
    parser.add_argument("--placeholders", action="store_true", help="Créer des images placeholder")
    args = parser.parse_args()
    
    log("🍭", "Fililico Landing Page Builder")
    log("─" * 40, "")
    
    if args.placeholders:
        try:
            create_placeholders()
        except ImportError:
            log("⚠️", "Pillow requis pour les placeholders: pip install Pillow")
    
    copy_assets()
    
    if args.deploy:
        deploy_to_gh_pages()
    else:
        log("💡", "Utilisez --deploy pour déployer vers gh-pages")
    
    log("─" * 40, "")
    log("✨", "Build terminé !")


if __name__ == "__main__":
    main()
