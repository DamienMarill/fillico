#!/usr/bin/env python3
"""
🍭 Fillico - Main Entry Point
Le filigrane n'est plus une corvée, c'est une friandise visuelle !
"""

import sys
import os
from pathlib import Path

# Fix Windows encoding issues (emojis in print statements)
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

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

        from ui.quick_mode import QuickModeApp

        app = QuickModeApp(file_path)
        result = app.run()
        sys.exit(0 if result and result.success else 1)
    else:
        # Mode normal: interface complète (pywebview)
        from ui import start_app
        start_app()
