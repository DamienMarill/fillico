# 🍭 Guide Utilisateur - Fililico

> _Le filigrane n'est plus une corvée, c'est une friandise visuelle !_

---

## Table des Matières

1. [Installation](#installation)
2. [Premier Lancement](#premier-lancement)
3. [Mode Application](#mode-application)
4. [Mode Quick (Clic Droit)](#mode-quick)
5. [Formats Supportés](#formats-supportés)
6. [FAQ](#faq)

---

## Installation

### Windows

1. Téléchargez `Fililico-Setup.exe` depuis les [Releases](https://github.com/marill-dev/fililico/releases)
2. Lancez l'installateur
3. Cochez "Ajouter au menu contextuel" pour activer le clic droit
4. Cliquez sur Installer !

### Linux

**AppImage (recommandé) :**

```bash
chmod +x Fililico-*.AppImage
./Fililico-*.AppImage
```

**Intégration système :**

```bash
python src/installer/linux_context_menu.py install
```

### macOS

1. Téléchargez `Fililico-*.dmg`
2. Glissez l'application dans le dossier Applications
3. Pour le menu contextuel : Préférences Système → Extensions → Finder

---

## Premier Lancement

Au lancement, Fililico affiche une interface kawaii avec :

- 🎀 **Header** : Logo et mascotte animée
- 📁 **Zone de dépôt** : Glissez vos fichiers ici
- ✏️ **Texte du filigrane** : "CONFIDENTIEL" par défaut
- 👁️ **Aperçu** : Prévisualisation en temps réel
- ✨ **Bouton Traitement** : Lance le filigranage

### La Mascotte

Notre adorable mascotte réagit à vos actions :

| État           | Expression | Signification                  |
| -------------- | ---------- | ------------------------------ |
| **Idle**       | ( • ᴗ • )  | En attente de fichiers         |
| **Drag**       | ( ◕ 0 ◕ )  | Prête à manger vos fichiers !  |
| **Processing** | ( >\_< )   | Elle travaille dur !           |
| **Done**       | ( ≧◡≦ )    | Filigrane ajouté avec succès ! |

---

## Mode Application

### Étape 1 : Ajouter des fichiers

- **Glisser-déposer** des fichiers sur la zone centrale
- Ou cliquez sur "Parcourir" pour sélectionner

### Étape 2 : Configurer le filigrane

- Modifiez le texte dans le champ prévu
- L'aperçu se met à jour en temps réel

### Étape 3 : Lancer le traitement

- Cliquez sur le bouton "✨ Filigraner!"
- Les fichiers traités sont créés avec le suffixe `_watermarked`

### Étape 4 : Récupérer vos fichiers

- Par défaut, les fichiers sont dans le même dossier que les originaux
- Vous pouvez changer le dossier de sortie dans les options

---

## Mode Quick

Le Mode Quick permet de filigraner rapidement via le menu contextuel.

### Utilisation

1. **Clic droit** sur un fichier image ou PDF
2. Sélectionnez "🍭 Ajouter un filigrane"
3. Entrez le texte (ou gardez "CONFIDENTIEL")
4. Appuyez sur **Entrée** ou cliquez sur "Filigraner!"

### Raccourcis clavier

| Touche   | Action             |
| -------- | ------------------ |
| `Entrée` | Valider et traiter |
| `Échap`  | Annuler            |

---

## Formats Supportés

### Images

| Format | Extension       | Notes                                |
| ------ | --------------- | ------------------------------------ |
| PNG    | `.png`          | Recommandé, conserve la transparence |
| JPEG   | `.jpg`, `.jpeg` | Compression avec perte               |
| BMP    | `.bmp`          | Non compressé                        |
| GIF    | `.gif`          | Première frame uniquement            |

### Documents

| Format | Extension | Notes                          |
| ------ | --------- | ------------------------------ |
| PDF    | `.pdf`    | Filigrane sur toutes les pages |

---

## FAQ

### Le filigrane est trop petit/grand ?

La taille est calculée automatiquement pour s'adapter à chaque image. Pour les fichiers très petits, le texte peut apparaître plus gros proportionnellement.

### Où sont mes fichiers traités ?

Par défaut, dans le même dossier que l'original avec le suffixe `_watermarked`. Exemple : `photo.png` → `photo_watermarked.png`

### Le menu clic droit n'apparaît pas ?

- **Windows** : Relancez l'installateur ou exécutez :

  ```bash
  python src/installer/windows_context_menu.py install
  ```

  (en tant qu'administrateur)

- **Linux** : Redémarrez Nautilus :

  ```bash
  nautilus -q
  ```

- **macOS** : Allez dans Préférences Système → Extensions → Finder

### Comment désinstaller ?

- **Windows** : Panneau de configuration → Programmes
- **Linux** : `python src/installer/linux_context_menu.py uninstall`
- **macOS** : Glissez l'app vers la corbeille

---

## Support

🐛 **Bug ?** Ouvrez une issue sur [GitHub](https://github.com/marill-dev/fililico/issues)

💡 **Idée ?** Les suggestions sont les bienvenues !

---

_Squish, Pop, Sparkle!_ ✨
