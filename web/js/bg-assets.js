/**
 * 🍭 Fillico - Background Assets Manager
 * Gère l'affichage aléatoire d'assets "retro gaming" en fond d'écran
 */

const ATLAS_CONFIG = {
    // 4x4 Grille principale
    cols: 4,
    rows: 4,
    // Configuration des sous-grilles pour chaque case (0-15)
    // [cols, rows]
    subgrids: [
        [4, 4], [2, 3], [3, 3], [2, 2],
        [4, 4], [4, 3], [3, 3], [3, 3],
        [2, 3], [4, 2], [3, 2], [2, 2],
        [4, 3], [3, 2], [3, 3], [2, 2]
    ],
    // Poids pour chaque type (index 0-15) - Plus le poids est haut, plus il a de chances d'apparaître
    weights: [
        12, 8, 8, 5,   // Ligne 1
        11, 7, 8, 10,   // Ligne 2
        7, 6, 6, 0,    // Ligne 3
        2, 2, 2, 2     // Ligne 4
    ]
};

class BgAssetManager {
    constructor() {
        this.container = null;
        this.assets = [];
        this.placedRects = []; // Pour gérer les collisions: {x, y, w, h}
        this.maxAssets = 20; // Nombre max d'assets à l'écran
        this.wrapperSize = 100; // Taille de base en px pour l'affichage
        this.atlasUrl = 'assets/images/assets.png';
    }

    init() {
        // Créer le conteneur s'il n'existe pas
        this.container = document.createElement('div');
        this.container.id = 'bg-assets-container';
        this.container.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
            overflow: hidden;
            pointer-events: none;
        `;
        document.body.appendChild(this.container);

        // Lancer la génération avec un petit délai pour être sûr que le DOM est prêt
        setTimeout(() => this.generateAssets(), 100);
        
        // Regénérer au resize pour éviter les placements bizarres
        window.addEventListener('resize', () => {
             // Debounce simple
             clearTimeout(this._resizeTimer);
             this._resizeTimer = setTimeout(() => this.generateAssets(), 500);
        });
    }

    /**
     * Choisit un index principal (0-15) en fonction des poids
     */
    getRandomTypeIndex() {
        const totalWeight = ATLAS_CONFIG.weights.reduce((sum, w) => sum + w, 0);
        let random = Math.random() * totalWeight;
        
        for (let i = 0; i < ATLAS_CONFIG.weights.length; i++) {
            random -= ATLAS_CONFIG.weights[i];
            if (random <= 0) {
                return i;
            }
        }
        return 0; // Fallback
    }

    /**
     * Génère une position CSS background-position pour un sprite donné
     * @param {number} typeIndex Index dans la grille principale (0-15)
     * @param {number} variantIndex Index dans la sous-grille (linéaire)
     */
    getSpriteStyle(typeIndex, variantIndex) {
        // 1. Calculer la position du Type dans la grille principale 4x4
        const mainCol = typeIndex % ATLAS_CONFIG.cols;
        const mainRow = Math.floor(typeIndex / ATLAS_CONFIG.cols);
        
        // Taille d'une case principale en % (100 / 4 = 25%)
        const mainSizePct = 100 / ATLAS_CONFIG.cols;

        // 2. Récupérer la config de la sous-grille
        const [subCols, subRows] = ATLAS_CONFIG.subgrids[typeIndex];
        
        // 3. Calculer la position de la variante dans la sous-grille
        const subCol = variantIndex % subCols;
        const subRow = Math.floor(variantIndex / subCols);

        // 4. Calculs magiques pour background-position et background-size
        // L'idée : On zoome sur la case principale, puis on décale pour afficher la bonne sous-case.
        // C'est complexe en CSS pur avec un seul fichier, on va plutôt utiliser un div avec overflow hidden 
        // et l'image en grand dedans, c'est plus simple pour gérer les ratios de sous-grilles variées.
        
        return {
            mainCol, mainRow, subCol, subRow, subCols, subRows
        };
    }

    createAssetElement(typeIndex) {
        // Choisir une variante au hasard
        const [subCols, subRows] = ATLAS_CONFIG.subgrids[typeIndex];
        const totalVariants = subCols * subRows;
        const variantIndex = Math.floor(Math.random() * totalVariants);
        
        // Calcul des coordonnées
        const mainCol = typeIndex % ATLAS_CONFIG.cols;
        const mainRow = Math.floor(typeIndex / ATLAS_CONFIG.cols);
        
        const subCol = variantIndex % subCols;
        const subRow = Math.floor(variantIndex / subCols);

        // Création du DOM - Structure à 2 niveaux pour séparer les animations :
        // <div class="bg-asset-float"> (animation flottante : float-v / float-h)
        //    <div class="bg-asset"> (animation bounce au clic + rotation)
        //       <img src="atlas" />
        //    </div>
        // </div>

        // === Wrapper externe pour l'animation de flottement ===
        const floatWrapper = document.createElement('div');
        floatWrapper.className = 'bg-asset-float';
        
        // Taille de base aléatoire pour la LARGEUR
        const scale = 0.5 + Math.random() * 0.7; // 0.5 à 1.2
        const width = this.wrapperSize * scale;
        
        // Calcul du ratio d'aspect (Largeur / Hauteur)
        const height = width * (subCols / subRows);
        
        floatWrapper.style.width = `${width}px`;
        floatWrapper.style.height = `${height-4}px`;
        floatWrapper.style.position = 'absolute';

        // === Wrapper interne pour le sprite + interactions ===
        const wrapper = document.createElement('div');
        wrapper.className = 'bg-asset';
        wrapper.style.width = '100%';
        wrapper.style.height = '100%';
        wrapper.style.position = 'relative';
        wrapper.style.overflow = 'hidden'; // Important pour cacher le reste de l'atlas
        
        // Image intérieure
        const img = document.createElement('img');
        img.src = this.atlasUrl;
        img.style.position = 'absolute';
        img.style.maxWidth = 'none';
        img.style.maxHeight = 'none';
        
        // Logique de zoom/découpage
        const mainCaseSize = width * subCols;
        const totalWidth = mainCaseSize * 4;
        const totalHeight = mainCaseSize * 4;
        
        img.style.width = `${totalWidth}px`;
        img.style.height = `${totalHeight}px`;
        
        // Position pour afficher le bon sprite
        const mainOffsetX = mainCol * mainCaseSize;
        const mainOffsetY = mainRow * mainCaseSize;
        const subOffsetX = subCol * width;
        const subOffsetY = subRow * height;
        
        const finalX = -(mainOffsetX + subOffsetX);
        const finalY = -(mainOffsetY + subOffsetY);
        
        img.style.transform = `translate(${finalX-4}px, ${finalY-2}px)`;
        img.style.left = '0';
        img.style.top = '0';
        
        wrapper.appendChild(img);
        floatWrapper.appendChild(wrapper);
        
        // Animation de flottement sur le wrapper EXTERNE
        const duration = 15 + Math.random() * 20; // 15-35s
        const delay = -Math.random() * 20;
        const direction = Math.random() > 0.5 ? 'float-v' : 'float-h';
        
        floatWrapper.style.animation = `${direction} ${duration}s ease-in-out infinite ${delay}s`;
        floatWrapper.style.opacity = '0.8';
        
        // Rotation statique + interactions sur le wrapper INTERNE
        const rot = Math.floor(Math.random() * 361);
        wrapper.style.setProperty('--rot', `${rot}deg`);
        wrapper.style.transform = `rotate(var(--rot))`;
        
        wrapper.style.pointerEvents = 'auto';
        wrapper.style.cursor = 'pointer';

        // Click bounce effect - sur le wrapper INTERNE uniquement
        wrapper.addEventListener('click', (e) => {
            e.stopPropagation();
            
            // Ajouter la classe bouncing pour déclencher l'animation CSS
            wrapper.classList.add('bouncing');
            
            // Retirer la classe après l'animation
            setTimeout(() => {
                wrapper.classList.remove('bouncing');
            }, 800);
        });
        
        return { element: floatWrapper, w: width, h: height };
    }

    checkCollision(rect) {
        // Marge de sécurité pour éviter que ça se touche
        const margin = 20;
        
        // 1. Check collisions avec les widgets centraux (approximatif)
        // On suppose que le contenu principal est centré
        const centerX = window.innerWidth / 2;
        const centerY = window.innerHeight / 2;
        const contentWidth = Math.min(window.innerWidth * 0.9, 1200); // Max container width
        const contentHeight = window.innerHeight * 0.8;
        
        const safeZone = {
            x: centerX - contentWidth / 2,
            y: centerY - contentHeight / 2,
            w: contentWidth,
            h: contentHeight
        };

        // Si on veut éviter le centre absolu :
        // if (rect.x < safeZone.x + safeZone.w &&
        //     rect.x + rect.w > safeZone.x &&
        //     rect.y < safeZone.y + safeZone.h &&
        //     rect.y + rect.h > safeZone.y) {
        //     return true;
        // }

        // 2. Check collisions avec les autres assets
        for (const other of this.placedRects) {
            if (rect.x < other.x + other.w + margin &&
                rect.x + rect.w > other.x - margin &&
                rect.y < other.y + other.h + margin &&
                rect.y + rect.h > other.y - margin) {
                return true;
            }
        }
        return false;
    }

    generateAssets() {
        if (!this.container) return;
        this.container.innerHTML = '';
        this.placedRects = [];
        this.assets = [];

        let attempts = 0;
        let count = 0;
        const maxAttempts = 1000;

        while (count < this.maxAssets && attempts < maxAttempts) {
            attempts++;
            
            const typeIndex = this.getRandomTypeIndex();
            const assetObj = this.createAssetElement(typeIndex);
            
            // Position aléatoire
            const x = (Math.random() * (window.innerWidth - assetObj.w));
            const y = Math.random() * (window.innerHeight - assetObj.h);
            
            const rect = { x, y, w: assetObj.w, h: assetObj.h };
            
            if (!this.checkCollision(rect)) {
                // Placer
                assetObj.element.style.left = `${x}px`;
                assetObj.element.style.top = `${y}px`;
                
                // La rotation est gérée par la variable CSS --rot définie dans createAssetElement
                
                this.container.appendChild(assetObj.element);
                this.placedRects.push(rect);
                count++;
            }
        }
    }
}

// Styles pour les animations
const styleSheet = document.createElement("style");
styleSheet.textContent = `
    @keyframes float-v {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-20px); }
    }
    @keyframes float-h {
        0%, 100% { transform: translateX(0); }
        50% { transform: translateX(15px); }
    }
`;
document.head.appendChild(styleSheet);

// Exporter l'instance
window.bgAssets = new BgAssetManager();
