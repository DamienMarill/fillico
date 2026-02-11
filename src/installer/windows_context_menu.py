r"""
🍭 Fillico - Windows Context Menu Integration
Script d'installation/désinstallation du menu contextuel Windows

Utilise HKEY_CURRENT_USER\Software\Classes\SystemFileAssociations
pour enregistrer le menu contextuel par extension de fichier.
Ne nécessite PAS de droits administrateur.
"""

import sys
import winreg
from pathlib import Path
from typing import List


class WindowsContextMenuInstaller:
    """
    Gère l'installation du menu contextuel Windows pour Fillico.
    Ajoute "Ajouter un filigrane" au clic droit sur les fichiers supportés.

    Utilise SystemFileAssociations sous HKCU pour :
    - Ne pas nécessiter de droits administrateur
    - Cibler uniquement les extensions supportées
    - Persister même si l'association par défaut change
    """

    # Extensions supportées
    SUPPORTED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".pdf"]

    # Nom du verbe dans le shell
    VERB_NAME = "Fillico"

    # Texte affiché dans le menu contextuel
    DISPLAY_TEXT = "Ajouter un filigrane"

    def __init__(self):
        """Initialise l'installateur."""
        self.app_path = self._get_app_path()

    def _get_app_path(self) -> Path:
        """Retourne le chemin de l'exécutable/script."""
        # En développement, utiliser le script Python quick_mode.py
        quick_mode_path = Path(__file__).parent.parent / "ui" / "quick_mode.py"
        if quick_mode_path.exists():
            return quick_mode_path

        # En production, chercher l'exécutable
        exe_path = Path(sys.executable).parent / "Fillico.exe"
        if exe_path.exists():
            return exe_path

        # Fallback sur le script même s'il n'existe pas encore
        return quick_mode_path

    def _get_python_path(self) -> str:
        """Retourne le chemin de pythonw.exe (sans console) ou python.exe en fallback."""
        python_dir = Path(sys.executable).parent
        pythonw = python_dir / "pythonw.exe"
        if pythonw.exists():
            return str(pythonw)
        return sys.executable

    def _get_icon_path(self) -> str:
        """Retourne le chemin de l'icône de l'application."""
        # Chercher fillico.ico à la racine du projet
        icon_path = Path(__file__).parent.parent.parent / "fillico.ico"
        if icon_path.exists():
            return str(icon_path.resolve())

        # Fallback sur assets
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icons" / "fillico.ico"
        if icon_path.exists():
            return str(icon_path.resolve())

        return ""

    def _get_registry_key_path(self, ext: str) -> str:
        r"""
        Retourne le chemin de la clé de registre pour une extension donnée.

        Utilise SystemFileAssociations sous HKCU :
        HKCU\Software\Classes\SystemFileAssociations\.ext\shell\Fillico
        """
        return rf"Software\Classes\SystemFileAssociations\{ext}\shell\{self.VERB_NAME}"

    def _get_command(self) -> str:
        """Retourne la commande à exécuter."""
        if self.app_path.suffix == ".py":
            # Mode développement - utiliser Python
            return f'"{self._get_python_path()}" "{self.app_path.resolve()}" "%1"'
        else:
            # Mode production - exécutable direct
            return f'"{self.app_path.resolve()}" --quick "%1"'

    def install(self) -> bool:
        """
        Installe le menu contextuel Windows pour chaque extension supportée.

        Returns:
            True si l'installation a réussi
        """
        try:
            command = self._get_command()
            icon_path = self._get_icon_path()
            installed_count = 0

            for ext in self.SUPPORTED_EXTENSIONS:
                key_path = self._get_registry_key_path(ext)
                command_key_path = key_path + r"\command"

                try:
                    # Créer la clé principale du shell pour cette extension
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                        # Nom affiché dans le menu contextuel
                        winreg.SetValue(key, "", winreg.REG_SZ, self.DISPLAY_TEXT)

                        # Icône
                        if icon_path:
                            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)

                    # Créer la clé command
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, command_key_path) as key:
                        winreg.SetValue(key, "", winreg.REG_SZ, command)

                    installed_count += 1
                    print(f"   ✅ {ext}")

                except Exception as e:
                    print(f"   ❌ {ext} : {e}")

            if installed_count > 0:
                print(f"\n✅ Menu contextuel installé pour {installed_count}/{len(self.SUPPORTED_EXTENSIONS)} extensions!")
                print(f"   Commande: {command}")
                print(f"\n💡 Ouvrez l'Explorateur et faites un clic droit sur une image ou un PDF.")
                return True
            else:
                print("❌ Aucune extension n'a pu être installée")
                return False

        except Exception as e:
            print(f"❌ Erreur lors de l'installation: {e}")
            return False

    def uninstall(self) -> bool:
        """
        Désinstalle le menu contextuel Windows pour toutes les extensions.

        Returns:
            True si la désinstallation a réussi
        """
        removed_count = 0

        for ext in self.SUPPORTED_EXTENSIONS:
            key_path = self._get_registry_key_path(ext)
            command_key_path = key_path + r"\command"

            # Supprimer la clé command d'abord (les sous-clés doivent être supprimées avant le parent)
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, command_key_path)
            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"   ⚠️ {ext}/command : {e}")

            # Puis la clé principale
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
                removed_count += 1
                print(f"   🗑️  {ext}")
            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"   ⚠️ {ext} : {e}")

        print(f"\n✅ Menu contextuel désinstallé ({removed_count} extensions nettoyées)")
        return True

    def is_installed(self) -> bool:
        """
        Vérifie si le menu contextuel est installé (au moins une extension).

        Returns:
            True si installé
        """
        for ext in self.SUPPORTED_EXTENSIONS:
            key_path = self._get_registry_key_path(ext)
            try:
                winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
                return True
            except FileNotFoundError:
                continue
        return False

    def status(self) -> dict:
        """
        Retourne l'état détaillé de l'installation.

        Returns:
            Dictionnaire {extension: bool (installée ou non)}
        """
        result = {}
        for ext in self.SUPPORTED_EXTENSIONS:
            key_path = self._get_registry_key_path(ext)
            try:
                winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
                result[ext] = True
            except FileNotFoundError:
                result[ext] = False
        return result


def main():
    """Point d'entrée pour l'installation/désinstallation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="🍭 Fillico - Gestionnaire du menu contextuel Windows"
    )
    parser.add_argument(
        "action",
        choices=["install", "uninstall", "status"],
        help="Action à effectuer",
    )
    args = parser.parse_args()

    installer = WindowsContextMenuInstaller()

    if args.action == "install":
        print("🍭 Fillico - Installation du menu contextuel Windows")
        print(f"   Python: {installer._get_python_path()}")
        print(f"   Script: {installer.app_path}")
        print(f"   Icône:  {installer._get_icon_path() or '(aucune)'}")
        print()
        installer.install()
    elif args.action == "uninstall":
        print("🍭 Fillico - Désinstallation du menu contextuel Windows")
        installer.uninstall()
    elif args.action == "status":
        print("🍭 Fillico - État du menu contextuel Windows\n")
        status = installer.status()
        for ext, installed in status.items():
            icon = "✅" if installed else "❌"
            print(f"   {icon} {ext}")

        if any(status.values()):
            print(f"\n📍 Registre: HKCU\\Software\\Classes\\SystemFileAssociations\\<ext>\\shell\\Fillico")
        else:
            print("\n❌ Le menu contextuel n'est pas installé. Lancez 'install' pour l'installer.")


if __name__ == "__main__":
    main()
