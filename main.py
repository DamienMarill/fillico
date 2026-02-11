#!/usr/bin/env python3
"""
🍭 Fillico - Main Entry Point
Le filigrane n'est plus une corvée, c'est une friandise visuelle !
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Support PyInstaller bundled path
if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS)
    if str(base_path / "src") not in sys.path:
        sys.path.insert(0, str(base_path / "src"))


if __name__ == "__main__":
    # Quick mode: lancé depuis le menu contextuel (clic droit)
    if "--quick" in sys.argv:
        idx = sys.argv.index("--quick")
        file_path = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None

        # Import direct sans passer par ui/__init__.py (qui charge eel)
        import importlib.util
        quick_mode_path = src_path / "ui" / "quick_mode.py"
        spec = importlib.util.spec_from_file_location("quick_mode", quick_mode_path)
        quick_mode = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(quick_mode)

        app = quick_mode.QuickModeApp(file_path)
        result = app.run()
        sys.exit(0 if result and result.success else 1)
    else:
        # Mode normal: interface complète
        from ui import start_app
        start_app()
