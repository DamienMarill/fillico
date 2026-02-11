"""
🍭 Fillico - UI Application
Point d'entrée de l'application avec Eel
"""

import sys
import subprocess
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# --- Windows: empêcher les fenêtres console flash ---
# Eel lance Chrome/Edge via subprocess.Popen sans CREATE_NO_WINDOW,
# ce qui provoque un flash de console. On monkey-patch Popen pour
# ajouter ce flag automatiquement sur Windows.
if sys.platform == "win32":
    _OriginalPopen = subprocess.Popen

    class _NoConsolePopen(_OriginalPopen):
        def __init__(self, *args, **kwargs):
            if "creationflags" not in kwargs:
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            super().__init__(*args, **kwargs)

    subprocess.Popen = _NoConsolePopen

import eel
from core import WatermarkEngine

# Initialize Eel with web folder
WEB_FOLDER = Path(__file__).parent.parent.parent / "web"
eel.init(str(WEB_FOLDER))

# Variable globale pour le fichier en cours de traitement
_current_file_path = None

def _pdf_progress_callback(current_page: int, total_pages: int):
    """Callback appelé pendant le traitement PDF pour envoyer la progression."""
    global _current_file_path
    if _current_file_path:
        # Envoyer la mise à jour au frontend via eel
        eel.onPdfProgress(_current_file_path, current_page, total_pages)()

# Global engine instance
engine = WatermarkEngine()
engine.set_progress_callback(_pdf_progress_callback)


@eel.expose
def get_app_version() -> str:
    """Retourne la version de l'application depuis pyproject.toml."""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    
    try:
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
            return data.get("project", {}).get("version", "1.0.0")
    except Exception:
        pass
    return "1.0.0"


@eel.expose
def get_default_output_folder() -> str:
    """Retourne le dossier home de l'utilisateur comme dossier de sortie par défaut."""
    return str(Path.home())


@eel.expose
def upload_file(filename: str, base64_content: str) -> dict:
    """
    Reçoit un fichier en base64 (drag&drop) et le sauvegarde dans un dossier temporaire.
    
    Args:
        filename: Nom du fichier original
        base64_content: Contenu du fichier encodé en base64
        
    Returns:
        Dictionnaire avec le chemin du fichier sauvegardé
    """
    import base64
    import tempfile
    
    try:
        # Créer un dossier temporaire pour les uploads
        temp_dir = Path(tempfile.gettempdir()) / "fillico_uploads"
        temp_dir.mkdir(exist_ok=True)
        
        # Décoder et sauvegarder le fichier
        file_data = base64.b64decode(base64_content)
        file_path = temp_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(file_data)
        
        return {
            "success": True,
            "path": str(file_path),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@eel.expose
def process_file(
    file_path: str,
    watermark_text: str = "CONFIDENTIEL",
    opacity: float = 0.5,
    output_folder: str = None,
) -> dict:
    """
    Traite un fichier (image ou PDF) avec un filigrane.

    Args:
        file_path: Chemin du fichier à traiter
        watermark_text: Texte du filigrane
        opacity: Opacité (0.0 à 1.0)
        output_folder: Dossier de sortie optionnel

    Returns:
        Dictionnaire avec le résultat du traitement
    """
    try:
        global _current_file_path
        # Définir le fichier en cours pour le callback de progression
        _current_file_path = file_path
        
        # Update engine settings
        engine.text = watermark_text
        engine.opacity = opacity

        # Calculate output path
        input_path = Path(file_path)
        if output_folder:
            output_path = Path(output_folder) / f"{input_path.stem}_watermarked{input_path.suffix}"
        else:
            output_path = None

        # Process
        result = engine.process(input_path, output_path)
        
        # Réinitialiser le fichier en cours
        _current_file_path = None

        if result.success:
            return {
                "success": True,
                "input": str(result.input_path.name),
                "output": str(result.output_path.name),
                "output_path": str(result.output_path),
            }
        else:
            return {
                "success": False,
                "input": str(result.input_path.name),
                "error": result.error,
            }

    except Exception as e:
        return {
            "success": False,
            "input": Path(file_path).name if file_path else "unknown",
            "error": str(e),
        }


@eel.expose
def generate_preview(file_path: str, watermark_text: str, opacity: float) -> dict:
    """
    Génère un aperçu du filigrane.

    Args:
        file_path: Chemin du fichier
        watermark_text: Texte du filigrane
        opacity: Opacité

    Returns:
        Dictionnaire avec l'image en base64
    """
    try:
        engine.text = watermark_text
        engine.opacity = opacity

        preview = engine.generate_preview(file_path)

        if preview:
            return {
                "success": True,
                "preview": preview,
            }
        else:
            return {
                "success": False,
                "error": "Format non supporté pour la prévisualisation",
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@eel.expose
def get_supported_formats() -> list:
    """Retourne la liste des formats supportés."""
    return list(engine.get_supported_extensions())


@eel.expose
def check_file_supported(file_path: str) -> bool:
    """Vérifie si un fichier est supporté."""
    return engine.is_supported(Path(file_path))


@eel.expose
def get_image_preview(file_path: str, max_size: int = 400) -> str:
    """
    Génère un aperçu base64 d'une image.
    
    Args:
        file_path: Chemin de l'image
        max_size: Taille maximale du côté le plus long
        
    Returns:
        Data URL base64 de l'image ou chaîne vide si erreur
    """
    import base64
    from io import BytesIO
    from PIL import Image
    
    try:
        path = Path(file_path)
        if not path.exists():
            return ""
        
        with Image.open(path) as img:
            # Redimensionner pour l'aperçu
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convertir en RGB si nécessaire (pour les PNG avec transparence)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Encoder en base64
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return f"data:image/jpeg;base64,{base64_data}"
    except Exception as e:
        print(f"Preview error: {e}")
        return ""


@eel.expose
def select_files() -> list:
    """
    Ouvre un dialogue pour sélectionner des fichiers à traiter.
    
    Returns:
        Liste des chemins de fichiers sélectionnés
    """
    import tkinter as tk
    from tkinter import filedialog
    
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    files = filedialog.askopenfilenames(
        title="Sélectionner des fichiers à filigraner",
        filetypes=[
            ("Tous les fichiers supportés", "*.png *.jpg *.jpeg *.bmp *.gif *.pdf"),
            ("Images", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("PDF", "*.pdf"),
        ]
    )
    
    root.destroy()
    return list(files) if files else []


@eel.expose
def select_output_folder(initial_dir: str = None) -> str:
    """
    Ouvre un dialogue pour sélectionner un dossier de sortie.
    
    Args:
        initial_dir: Dossier initial à afficher
        
    Returns:
        Chemin du dossier sélectionné ou chaîne vide si annulé
    """
    import tkinter as tk
    from tkinter import filedialog
    
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    root.attributes('-topmost', True)  # Mettre au premier plan
    
    folder = filedialog.askdirectory(
        title="Sélectionner le dossier de destination",
        initialdir=initial_dir if initial_dir else None,
    )
    
    root.destroy()
    return folder or ""


@eel.expose
def get_file_directory(file_path: str) -> str:
    """
    Retourne le dossier parent d'un fichier.
    
    Args:
        file_path: Chemin du fichier
        
    Returns:
        Chemin du dossier parent
    """
    return str(Path(file_path).parent)


@eel.expose
def get_file_info(file_path: str) -> dict:
    """
    Récupère les informations d'un fichier (taille, etc).
    
    Args:
        file_path: Chemin du fichier
        
    Returns:
        Dictionnaire avec les infos du fichier
    """
    try:
        path = Path(file_path)
        if path.exists():
            stat = path.stat()
            return {
                "size": stat.st_size,
                "exists": True,
            }
        return {"size": 0, "exists": False}
    except Exception:
        return {"size": 0, "exists": False}


def start_app():
    """Démarre l'application Eel."""
    print("🍭 Fillico - Démarrage...")

    try:
        # Start Eel with default browser
        eel.start(
            "index.html",
            size=(1200, 800),
            position=(100, 100),
            mode="chrome",  # or 'edge', 'default'
        )
    except (SystemExit, MemoryError, KeyboardInterrupt):
        pass
    except Exception as e:
        print(f"❌ Erreur: {e}")
        # Fallback to default browser
        eel.start("index.html", mode="default")


if __name__ == "__main__":
    start_app()
