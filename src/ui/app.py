"""
🍭 Fillico - UI Application
Point d'entrée de l'application avec pywebview
"""

import sys
import json
import threading
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import webview
from core import WatermarkEngine


class FillicoAPI:
    """API Python exposée au JavaScript via pywebview."""

    def __init__(self):
        self._window = None
        self._engine = WatermarkEngine()
        self._engine.set_progress_callback(self._pdf_progress_callback)
        self._current_file_path = None

    def set_window(self, window):
        """Définit la fenêtre pywebview (appelé après création)."""
        self._window = window

    def _pdf_progress_callback(self, current_page: int, total_pages: int):
        """Callback de progression PDF — appelle JS depuis un thread."""
        if self._window and self._current_file_path:
            # Échapper le chemin pour JS
            safe_path = self._current_file_path.replace("\\", "\\\\").replace("'", "\\'")
            self._window.evaluate_js(
                f"onPdfProgress('{safe_path}', {current_page}, {total_pages})"
            )

    # ═══════════════════════════════════════════════════════════════
    # API exposée au JavaScript
    # ═══════════════════════════════════════════════════════════════

    def get_app_version(self) -> str:
        """Retourne la version de l'application depuis pyproject.toml."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                return "1.0.0"

        try:
            pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                return data.get("project", {}).get("version", "1.0.0")
        except Exception:
            pass
        return "1.0.0"

    def get_default_output_folder(self) -> str:
        """Retourne le dossier home comme dossier de sortie par défaut."""
        return str(Path.home())

    def upload_file(self, filename: str, base64_content: str) -> dict:
        """Reçoit un fichier en base64 (drag&drop) et le sauvegarde temporairement."""
        import base64
        import tempfile

        try:
            temp_dir = Path(tempfile.gettempdir()) / "fillico_uploads"
            temp_dir.mkdir(exist_ok=True)

            file_data = base64.b64decode(base64_content)
            file_path = temp_dir / filename

            with open(file_path, "wb") as f:
                f.write(file_data)

            return {"success": True, "path": str(file_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def process_file(
        self,
        file_path: str,
        watermark_text: str = "CONFIDENTIEL",
        opacity: float = 0.5,
        output_folder: str = None,
    ) -> dict:
        """Traite un fichier (image ou PDF) avec un filigrane."""
        try:
            self._current_file_path = file_path

            self._engine.text = watermark_text
            self._engine.opacity = opacity

            input_path = Path(file_path)
            if output_folder:
                output_path = (
                    Path(output_folder)
                    / f"{input_path.stem}_watermarked{input_path.suffix}"
                )
            else:
                output_path = None

            result = self._engine.process(input_path, output_path)

            self._current_file_path = None

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

    def generate_preview(
        self, file_path: str, watermark_text: str, opacity: float
    ) -> dict:
        """Génère un aperçu du filigrane."""
        try:
            self._engine.text = watermark_text
            self._engine.opacity = opacity

            preview = self._engine.generate_preview(file_path)

            if preview:
                return {"success": True, "preview": preview}
            else:
                return {
                    "success": False,
                    "error": "Format non supporté pour la prévisualisation",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_supported_formats(self) -> list:
        """Retourne la liste des formats supportés."""
        return list(self._engine.get_supported_extensions())

    def check_file_supported(self, file_path: str) -> bool:
        """Vérifie si un fichier est supporté."""
        return self._engine.is_supported(Path(file_path))

    def get_image_preview(self, file_path: str, max_size: int = 400) -> str:
        """Génère un aperçu base64 d'une image."""
        import base64
        from io import BytesIO
        from PIL import Image

        try:
            path = Path(file_path)
            if not path.exists():
                return ""

            with Image.open(path) as img:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

                return f"data:image/jpeg;base64,{base64_data}"
        except Exception as e:
            print(f"Preview error: {e}")
            return ""

    def select_files(self) -> list:
        """Ouvre un dialogue natif pour sélectionner des fichiers."""
        if self._window:
            result = self._window.create_file_dialog(
                webview.OPEN_DIALOG,
                allow_multiple=True,
                file_types=(
                    "Fichiers supportés (*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.pdf)",
                    "Images (*.png;*.jpg;*.jpeg;*.bmp;*.gif)",
                    "PDF (*.pdf)",
                ),
            )
            return list(result) if result else []
        return []

    def select_output_folder(self, initial_dir: str = None) -> str:
        """Ouvre un dialogue natif pour sélectionner un dossier."""
        if self._window:
            result = self._window.create_file_dialog(
                webview.FOLDER_DIALOG,
                directory=initial_dir or "",
            )
            return result[0] if result else ""
        return ""

    def get_file_directory(self, file_path: str) -> str:
        """Retourne le dossier parent d'un fichier."""
        return str(Path(file_path).parent)

    def get_file_info(self, file_path: str) -> dict:
        """Récupère les informations d'un fichier."""
        try:
            path = Path(file_path)
            if path.exists():
                stat = path.stat()
                return {"size": stat.st_size, "exists": True}
            return {"size": 0, "exists": False}
        except Exception:
            return {"size": 0, "exists": False}

def _set_window_icon_windows(icon_path: str, title: str):
    """Applique l'icône de la fenêtre via Win32 API (pywebview ne le supporte pas sur Windows)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import wintypes
        import time

        user32 = ctypes.windll.user32
        IMAGE_ICON = 1
        LR_LOADFROMFILE = 0x0010
        LR_DEFAULTSIZE = 0x0040
        WM_SETICON = 0x0080
        ICON_SMALL = 0
        ICON_BIG = 1

        # Charger l'icône depuis le fichier
        hicon = user32.LoadImageW(
            0, icon_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE
        )
        if not hicon:
            return

        # Trouver la fenêtre par titre (attendre qu'elle soit créée)
        for _ in range(20):
            hwnd = user32.FindWindowW(None, title)
            if hwnd:
                user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon)
                user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon)
                return
            time.sleep(0.25)
    except Exception as e:
        print(f"Icon error: {e}")


def start_app():
    """Démarre l'application pywebview."""
    # Identifier l'app comme "Fillico" dans la barre des tâches Windows
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("fillico.app")

    print("Fillico - Demarrage...")

    api = FillicoAPI()

    # Résoudre les chemins
    base_dir = Path(__file__).parent.parent.parent
    if getattr(sys, "frozen", False):
        base_dir = Path(sys._MEIPASS)

    web_folder = base_dir / "web"
    icon_path = base_dir / "fillico.ico"

    title = "🍭 Fillico - Filigraner Illico!"

    window = webview.create_window(
        title,
        url=str(web_folder / "index.html"),
        js_api=api,
        width=1200,
        height=800,
        min_size=(800, 600),
    )

    api.set_window(window)

    # Appliquer l'icône via Win32 API dans un thread séparé
    if sys.platform == "win32" and icon_path.exists():
        import threading
        threading.Thread(
            target=_set_window_icon_windows,
            args=(str(icon_path), title),
            daemon=True,
        ).start()

    webview.start(debug=False)


if __name__ == "__main__":
    start_app()
