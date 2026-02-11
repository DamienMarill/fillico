"""
🍭 Fillico - Quick Mode UI
Interface minimaliste Tkinter pour le filigranage rapide via clic droit
"""

import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import WatermarkEngine


class QuickModeApp:
    """
    Interface minimaliste pour le filigranage rapide.
    Utilisée via le menu contextuel (clic droit).
    """

    # Dimensions de la fenêtre
    WIDTH = 440
    HEIGHT = 320

    # Couleurs kawaii
    COLORS = {
        "bg": "#fdf2f8",           # Cotton Cloud
        "primary": "#f472b6",      # Bubblegum Pink
        "secondary": "#a78bfa",    # Magic Berry
        "text": "#4c1d95",         # Deep Grape
        "text_light": "#7c3aed",   # Soft Grape
        "success_bg": "#ecfdf5",   # Mint Cloud
        "success_fg": "#059669",   # Fresh Mint
        "success_border": "#a7f3d0",  # Minty Fresh
        "error_bg": "#fef2f2",     # Rose Cloud
        "error_fg": "#dc2626",     # Cherry Red
        "error_border": "#fecaca", # Soft Cherry
        "warning_fg": "#d97706",   # Amber
        "progress_bg": "#e5e7eb",  # Soft Gray
        "progress_fg": "#a78bfa",  # Magic Berry
    }

    def __init__(self, file_path: Optional[str] = None):
        """
        Initialise l'interface Quick Mode.

        Args:
            file_path: Chemin du fichier à traiter (passé par le menu contextuel)
        """
        self.file_path = Path(file_path) if file_path else None
        self.engine = WatermarkEngine()
        self.result = None
        self._processing = False

        # Création de la fenêtre
        self.root = tk.Tk()
        self._setup_window()
        self._create_widgets()
        self._bind_events()

    def _setup_window(self):
        """Configure la fenêtre principale."""
        self.root.title("🍭 Fillico - Quick Mode")
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=self.COLORS["bg"])

        # Centrer la fenêtre
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.WIDTH) // 2
        y = (self.root.winfo_screenheight() - self.HEIGHT) // 2
        self.root.geometry(f"+{x}+{y}")

        # Garder la fenêtre au premier plan
        self.root.attributes("-topmost", True)

        # Icône (si disponible)
        try:
            icon_path = Path(__file__).parent.parent.parent / "fillico.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass

    def _create_widgets(self):
        """Crée les widgets de l'interface."""
        # Frame principal avec padding
        self.main_frame = tk.Frame(self.root, bg=self.COLORS["bg"], padx=20, pady=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # === Titre ===
        title_label = tk.Label(
            self.main_frame,
            text="🍭 Filigraner Illico!",
            font=("Segoe UI", 14, "bold"),
            fg=self.COLORS["primary"],
            bg=self.COLORS["bg"],
        )
        title_label.pack(pady=(0, 8))

        # === Nom du fichier ===
        if self.file_path:
            file_frame = tk.Frame(self.main_frame, bg=self.COLORS["bg"])
            file_frame.pack(fill=tk.X, pady=(0, 8))

            file_label = tk.Label(
                file_frame,
                text=f"📄 {self.file_path.name}",
                font=("Segoe UI", 9),
                fg=self.COLORS["text_light"],
                bg=self.COLORS["bg"],
                anchor=tk.W,
            )
            file_label.pack(anchor=tk.W)

            # Dossier parent (tronqué si trop long)
            parent_str = str(self.file_path.parent)
            if len(parent_str) > 50:
                parent_str = "..." + parent_str[-47:]
            folder_label = tk.Label(
                file_frame,
                text=f"📁 {parent_str}",
                font=("Segoe UI", 8),
                fg="#9ca3af",
                bg=self.COLORS["bg"],
                anchor=tk.W,
            )
            folder_label.pack(anchor=tk.W)

        # === Champ de saisie ===
        input_frame = tk.Frame(self.main_frame, bg=self.COLORS["bg"])
        input_frame.pack(fill=tk.X, pady=(5, 0))

        text_label = tk.Label(
            input_frame,
            text="Texte du filigrane :",
            font=("Segoe UI", 10),
            fg=self.COLORS["text"],
            bg=self.COLORS["bg"],
        )
        text_label.pack(anchor=tk.W)

        self.text_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 11),
            fg=self.COLORS["text"],
            bg="white",
            relief=tk.FLAT,
            highlightthickness=2,
            highlightbackground=self.COLORS["secondary"],
            highlightcolor=self.COLORS["primary"],
        )
        self.text_entry.insert(0, "CONFIDENTIEL")
        self.text_entry.pack(fill=tk.X, pady=5, ipady=5)
        self.text_entry.focus_set()
        self.text_entry.select_range(0, tk.END)

        # === Boutons ===
        button_frame = tk.Frame(self.main_frame, bg=self.COLORS["bg"])
        button_frame.pack(fill=tk.X, pady=(12, 0))

        # Bouton Annuler
        self.cancel_btn = tk.Button(
            button_frame,
            text="❌ Annuler",
            font=("Segoe UI", 10),
            fg=self.COLORS["text"],
            bg="white",
            activebackground=self.COLORS["bg"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8,
            command=self._cancel,
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Bouton Filigraner
        self.submit_btn = tk.Button(
            button_frame,
            text="✨ Filigraner!",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg=self.COLORS["primary"],
            activebackground=self.COLORS["secondary"],
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8,
            command=self._process,
        )
        self.submit_btn.pack(side=tk.RIGHT)

        # === Zone de feedback (initialement cachée) ===
        self.feedback_frame = tk.Frame(self.main_frame, bg=self.COLORS["bg"])
        self.feedback_frame.pack(fill=tk.X, pady=(12, 0))

        # Barre de progression
        self.progress_frame = tk.Frame(self.feedback_frame, bg=self.COLORS["bg"])

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Fillico.Horizontal.TProgressbar",
            troughcolor=self.COLORS["progress_bg"],
            background=self.COLORS["progress_fg"],
            thickness=6,
        )
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            style="Fillico.Horizontal.TProgressbar",
            mode="indeterminate",
            length=380,
        )

        self.progress_label = tk.Label(
            self.progress_frame,
            text="",
            font=("Segoe UI", 9),
            fg=self.COLORS["text_light"],
            bg=self.COLORS["bg"],
        )

        # Compteur de pages (sous la barre)
        self.page_label = tk.Label(
            self.progress_frame,
            text="",
            font=("Segoe UI", 9),
            fg=self.COLORS["text_light"],
            bg=self.COLORS["bg"],
        )

        # Zone de résultat (succès ou erreur)
        self.result_frame = tk.Frame(
            self.feedback_frame,
            bg=self.COLORS["success_bg"],
            padx=12,
            pady=10,
            highlightthickness=1,
            highlightbackground=self.COLORS["success_border"],
        )

        self.result_icon_label = tk.Label(
            self.result_frame,
            text="",
            font=("Segoe UI", 16),
            bg=self.COLORS["success_bg"],
        )

        # Frame texte (créé UNE SEULE FOIS pour éviter le bug de layout)
        self.result_text_frame = tk.Frame(self.result_frame, bg=self.COLORS["success_bg"])

        self.result_title_label = tk.Label(
            self.result_text_frame,
            text="",
            font=("Segoe UI", 10, "bold"),
            fg=self.COLORS["success_fg"],
            bg=self.COLORS["success_bg"],
            anchor=tk.W,
        )

        self.result_detail_label = tk.Label(
            self.result_text_frame,
            text="",
            font=("Segoe UI", 9),
            fg=self.COLORS["text_light"],
            bg=self.COLORS["success_bg"],
            anchor=tk.W,
            wraplength=360,
            justify=tk.LEFT,
        )

    def _bind_events(self):
        """Lie les événements clavier."""
        self.root.bind("<Return>", lambda e: self._process())
        self.root.bind("<Escape>", lambda e: self._cancel())

    def _show_progress(self, message: str = "Traitement en cours..."):
        """Affiche la barre de progression."""
        # Cacher le résultat précédent
        self.result_frame.pack_forget()

        # Afficher la progression
        self.progress_frame.pack(fill=tk.X, pady=(0, 5))
        self.progress_label.config(text=f"⏳ {message}")
        self.progress_label.pack(anchor=tk.W, pady=(0, 4))
        self.progress_bar.pack(fill=tk.X)
        self.page_label.config(text="")
        self.page_label.pack(anchor=tk.W, pady=(4, 0))
        self.progress_bar.start(15)

    def _update_progress(self, current: int, total: int):
        """Met à jour le compteur de pages (appelé depuis le thread de traitement)."""
        self.root.after(0, self._update_progress_ui, current, total)

    def _update_progress_ui(self, current: int, total: int):
        """Met à jour l'UI du compteur de pages (thread principal)."""
        self.page_label.config(text=f"📄 Page {current}/{total}")
        self.root.update_idletasks()

    def _hide_progress(self):
        """Cache la barre de progression."""
        self.progress_bar.stop()
        self.progress_frame.pack_forget()

    def _show_result(self, success: bool, title: str, detail: str = ""):
        """Affiche le résultat inline (succès ou erreur)."""
        self._hide_progress()

        if success:
            bg = self.COLORS["success_bg"]
            fg = self.COLORS["success_fg"]
            border = self.COLORS["success_border"]
            icon = "✅"
        else:
            bg = self.COLORS["error_bg"]
            fg = self.COLORS["error_fg"]
            border = self.COLORS["error_border"]
            icon = "❌"

        # Configurer le style de tous les éléments
        self.result_frame.config(bg=bg, highlightbackground=border)
        self.result_icon_label.config(text=icon, bg=bg)
        self.result_text_frame.config(bg=bg)
        self.result_title_label.config(text=title, fg=fg, bg=bg)
        self.result_detail_label.config(text=detail, bg=bg)

        # Packer les éléments (idempotent grâce à pack_forget d'abord)
        self.result_icon_label.pack_forget()
        self.result_text_frame.pack_forget()
        self.result_title_label.pack_forget()
        self.result_detail_label.pack_forget()

        self.result_frame.pack(fill=tk.X)
        self.result_icon_label.pack(side=tk.LEFT, padx=(0, 8), anchor=tk.N)
        self.result_text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.result_title_label.pack(anchor=tk.W)
        if detail:
            self.result_detail_label.pack(anchor=tk.W, pady=(2, 0))

        # Agrandir la fenêtre si nécessaire
        self.root.update_idletasks()
        height_needed = self.main_frame.winfo_reqheight() + 30
        if height_needed > self.HEIGHT:
            self.root.geometry(f"{self.WIDTH}x{height_needed}")

    def _show_warning(self, message: str):
        """Affiche un avertissement inline."""
        self._show_result(False, message)

    def _process(self):
        """Traite le fichier avec le filigrane."""
        if self._processing:
            return

        text = self.text_entry.get().strip()

        if not text:
            self._show_warning("Le texte du filigrane ne peut pas être vide !")
            return

        if not self.file_path:
            self._show_result(False, "Aucun fichier spécifié !")
            return

        if not self.file_path.exists():
            self._show_result(
                False,
                "Fichier introuvable",
                str(self.file_path),
            )
            return

        # Verrouiller l'UI pendant le traitement
        self._processing = True
        self.submit_btn.config(state=tk.DISABLED, text="⏳ Traitement...")
        self.cancel_btn.config(state=tk.DISABLED)
        self.text_entry.config(state=tk.DISABLED)

        # Afficher la progression
        self._show_progress(f"Filigranage de {self.file_path.name}...")

        # Brancher le callback de progression pour les PDFs
        self.engine.set_progress_callback(self._update_progress)

        # Lancer le traitement dans un thread séparé pour ne pas bloquer l'UI
        thread = threading.Thread(target=self._process_thread, args=(text,), daemon=True)
        thread.start()

    def _process_thread(self, text: str):
        """Thread de traitement du fichier."""
        try:
            self.engine.text = text

            # Pour les images, afficher 1/1 directement
            file_type = self.engine.get_file_type(self.file_path)
            if str(file_type.value) != "pdf":
                self._update_progress(1, 1)

            result = self.engine.process(self.file_path)

            # Retourner au thread principal pour mettre à jour l'UI
            self.root.after(0, self._on_process_complete, result, None)

        except Exception as e:
            self.root.after(0, self._on_process_complete, None, e)

    def _on_process_complete(self, result, error):
        """Callback appelé après le traitement (dans le thread principal)."""
        self._processing = False

        if error:
            self._show_result(
                False,
                "Une erreur est survenue",
                str(error),
            )
            self._reset_buttons()
            return

        if result and result.success:
            self.result = result
            output_name = result.output_path.name
            output_dir = str(result.output_path.parent)
            if len(output_dir) > 45:
                output_dir = "..." + output_dir[-42:]

            self._show_result(
                True,
                "Filigrane ajouté avec succès !",
                f"📄 {output_name}\n📁 {output_dir}",
            )

            # Changer le bouton Annuler en "Fermer"
            self.cancel_btn.config(
                state=tk.NORMAL,
                text="👋 Fermer",
                command=self._cancel,
            )
            # Garder le bouton submit désactivé
            self.submit_btn.config(text="✅ Terminé!")

        else:
            error_msg = result.error if result else "Erreur inconnue"
            self._show_result(
                False,
                "Impossible de traiter le fichier",
                error_msg,
            )
            self._reset_buttons()

    def _reset_buttons(self):
        """Réactive les boutons après un échec."""
        self.submit_btn.config(state=tk.NORMAL, text="✨ Filigraner!")
        self.cancel_btn.config(state=tk.NORMAL)
        self.text_entry.config(state=tk.NORMAL)
        self.text_entry.focus_set()

    def _cancel(self):
        """Annule et ferme la fenêtre."""
        self.root.quit()

    def run(self):
        """Lance l'application."""
        self.root.mainloop()
        try:
            self.root.destroy()
        except Exception:
            pass
        return self.result


def main():
    """Point d'entrée pour le mode Quick."""
    # Récupérer le fichier passé en argument
    file_path = sys.argv[1] if len(sys.argv) > 1 else None

    if not file_path:
        # Mode démo sans fichier
        print("🍭 Fillico Quick Mode")
        print("Usage: python quick_mode.py <fichier>")
        print("\nLancement en mode démo...")

    app = QuickModeApp(file_path)
    result = app.run()

    if result and result.success:
        print(f"✅ Fichier créé: {result.output_path}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
