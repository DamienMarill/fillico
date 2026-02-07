# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versionnement Sémantique](https://semver.org/lang/fr/).

## [1.0.0] - 2026-02-07

### 🎉 Première Release !

Application desktop multi-plateforme de filigranage avec style **Kawaii Pop**.

### ✨ Ajouté

#### Core Engine

- Support images : PNG, JPG, JPEG, BMP, GIF
- Support PDF : filigrane sur toutes les pages
- Calcul dynamique de la taille du texte
- Opacité configurable (50% par défaut)
- Génération de previews en temps réel

#### Interface Web

- Design "Candy Shop" avec glassmorphism
- Drag & drop interactif
- Mascotte animée (4 états : Idle, Drag, Processing, Done)
- Notifications toast
- Barre de progression

#### Mode Quick

- Interface Tkinter minimaliste (420x180px)
- Raccourcis clavier (Entrée/Échap)
- Texte pré-rempli "CONFIDENTIEL"

#### Intégration Système

- **Windows** : Menu contextuel via registre
- **Linux** : Scripts Nautilus (GNOME) et Dolphin (KDE)
- **macOS** : Quick Action Finder Services

#### CI/CD

- Tests automatisés avec pytest
- Build multi-plateforme (Windows, Linux, macOS)
- Release automatique via GitHub Actions

#### Installateurs

- Inno Setup (Windows .exe)
- AppImage (Linux)
- DMG (macOS)

### 📁 Structure

```
fililico/
├── src/core/       # Moteur de filigranage
├── src/ui/         # Interfaces (Web + Quick)
├── src/installer/  # Intégration système
├── web/            # Frontend kawaii
├── tests/          # Tests unitaires
└── docs/           # Documentation
```

---

_Squish, Pop, Sparkle!_ 🍭
