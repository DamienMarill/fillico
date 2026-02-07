# 🛠️ Guide Développeur - Fililico

> Documentation technique pour les contributeurs

---

## Table des Matières

1. [Architecture](#architecture)
2. [Installation Dev](#installation-dev)
3. [Structure du Code](#structure-du-code)
4. [Core Engine](#core-engine)
5. [Interfaces](#interfaces)
6. [Tests](#tests)
7. [Build & Release](#build--release)
8. [Contribution](#contribution)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Fililico                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Mode Quick │  │  Interface  │  │   Menu Contextuel   │  │
│  │  (Tkinter)  │  │  Web (Eel)  │  │  (Windows/Linux/    │  │
│  │             │  │             │  │   macOS)            │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │             │
│         └────────────────┼─────────────────────┘             │
│                          │                                   │
│                   ┌──────▼──────┐                            │
│                   │    Core     │                            │
│                   │   Engine    │                            │
│                   └──────┬──────┘                            │
│                          │                                   │
│         ┌────────────────┼────────────────┐                  │
│         │                │                │                  │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐          │
│  │   Image     │  │    PDF      │  │   Future    │          │
│  │  Processor  │  │  Processor  │  │  Processors │          │
│  │  (Pillow)   │  │  (PyPDF2)   │  │             │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation Dev

### Prérequis

- Python 3.11+
- pip / pipenv

### Setup

```bash
# Cloner le repo
git clone https://github.com/marill-dev/fililico.git
cd fililico

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate   # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python main.py
```

---

## Structure du Code

```
fililico/
├── main.py                 # Point d'entrée principal
├── src/
│   ├── core/               # Logique métier
│   │   ├── __init__.py
│   │   ├── watermark_engine.py   # Moteur principal
│   │   ├── image_processor.py    # Traitement images
│   │   └── pdf_processor.py      # Traitement PDF
│   ├── ui/                 # Interfaces utilisateur
│   │   ├── app.py          # Bridge Eel (interface web)
│   │   └── quick_mode.py   # Interface Tkinter
│   └── installer/          # Intégration système
│       ├── windows_context_menu.py
│       ├── linux_context_menu.py
│       └── macos_context_menu.py
├── web/                    # Frontend
│   ├── index.html
│   ├── css/
│   │   ├── variables.css   # Design tokens
│   │   ├── components.css  # Composants
│   │   └── layout.css      # Structure
│   └── js/
│       └── app.js          # Logique frontend
├── tests/                  # Tests unitaires
└── resources/              # Ressources de build
```

---

## Core Engine

### WatermarkEngine

Classe principale orchestrant les processeurs.

```python
from src.core import WatermarkEngine

engine = WatermarkEngine(text="CONFIDENTIEL", opacity=0.5)

# Traiter un fichier
result = engine.process(Path("document.pdf"))

if result.success:
    print(f"Fichier créé : {result.output_path}")
else:
    print(f"Erreur : {result.error}")
```

### API

| Méthode                      | Description                                         |
| ---------------------------- | --------------------------------------------------- |
| `process(path)`              | Traite un fichier et retourne un `ProcessingResult` |
| `preview(path)`              | Génère un aperçu base64                             |
| `is_supported(path)`         | Vérifie si le format est supporté                   |
| `get_supported_extensions()` | Liste des extensions supportées                     |

### ProcessingResult

```python
@dataclass
class ProcessingResult:
    input_path: Path
    output_path: Optional[Path]
    success: bool
    error: Optional[str]
    file_type: FileType
```

---

## Interfaces

### Interface Web (Eel)

Le bridge Python-JS utilise Eel pour exposer les fonctions Python au frontend.

**Python → JavaScript :**

```python
@eel.expose
def process_files(file_paths: List[str], text: str) -> dict:
    # Traitement...
    return {"success": True, "results": [...]}
```

**JavaScript → Python :**

```javascript
const result = await eel.process_files(files, text)();
```

### Mode Quick (Tkinter)

Interface minimaliste pour le menu contextuel.

```python
from src.ui.quick_mode import QuickModeApp

app = QuickModeApp(file_path="/path/to/file.png")
result = app.run()
```

---

## Tests

### Lancer les tests

```bash
# Tous les tests
python -m pytest tests/ -v

# Avec couverture
python -m pytest tests/ --cov=src --cov-report=html

# Un test spécifique
python -m pytest tests/test_core.py::TestWatermarkEngine -v
```

### Structure des tests

```python
class TestWatermarkEngine:
    def test_init_with_defaults(self):
        engine = WatermarkEngine()
        assert engine.text == "CONFIDENTIEL"

    def test_process_unsupported_file(self):
        engine = WatermarkEngine()
        result = engine.process(Path("test.txt"))
        assert result.success is False
```

---

## Build & Release

### Build local

```bash
# Windows
python -m PyInstaller fililico.spec --clean

# Ou via le script
python build.py build
```

### Créer une release

1. Mettre à jour la version dans `main.py`
2. Mettre à jour `CHANGELOG.md`
3. Créer un tag : `git tag v1.0.0`
4. Push : `git push origin v1.0.0`

GitHub Actions génère automatiquement :

- `Fililico.exe` (Windows)
- `Fililico` (Linux)
- `Fililico` (macOS)

---

## Contribution

### Workflow

1. Fork le repo
2. Créer une branche : `git checkout -b feature/ma-feature`
3. Commiter : `git commit -m "✨ Add feature"`
4. Push : `git push origin feature/ma-feature`
5. Ouvrir une Pull Request

### Conventions de commit

| Emoji | Type                    |
| ----- | ----------------------- |
| ✨    | Nouvelle fonctionnalité |
| 🐛    | Correction de bug       |
| 📝    | Documentation           |
| 🎨    | Style / UI              |
| ♻️    | Refactoring             |
| 🧪    | Tests                   |

### Style de code

- Python : Black + isort
- JavaScript : Prettier
- Docstrings Google-style

---

_Questions ? Ouvrez une issue !_ 🍭
