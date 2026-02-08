import os
import numpy as np
from PIL import Image

def process_assets(input_path="assets.jpeg", output_path="assets_no_bg.png", threshold=30):
    """
    Traite uniquement assets.jpeg pour retirer le fond noir.
    """
    if not os.path.exists(input_path):
        print(f"Oups ! Impossible de trouver {input_path} (｡•́︿•̀｡)")
        return

    print(f"Traitement de {input_path} vers {output_path} en cours... (ﾉ^ヮ^)ﾉ*:・ﾟ✧")
    
    try:
        # Chargement de l'image et conversion en RGBA (pour la transparence)
        img = Image.open(input_path).convert("RGBA")
        data = np.array(img)

        # Création du masque pour les pixels "noirs" (inférieurs au seuil)
        # On transpose pour avoir (channels, rows, cols)
        r, g, b, a = data.T
        black_mask = (r < threshold) & (g < threshold) & (b < threshold)
        
        # On met l'alpha à 0 pour les pixels noirs
        # On transpose le masque pour matcher (rows, cols)
        data[..., 3][black_mask.T] = 0
        
        # Création de la nouvelle image
        new_img = Image.fromarray(data)
        
        # Optionnel : Recadrage automatique (désactivé pour garder la taille d'origine)
        # bbox = new_img.getbbox()
        # if bbox:
        #     new_img = new_img.crop(bbox)
        #     print(f"  Recadré selon {bbox}")
        # else:
        #     print("  Attention : L'image semble vide après traitement !")
        
        new_img.save(output_path)
        print(f"C'est fait ! Sauvegardé sous {output_path} (≧◡≦)")

    except Exception as e:
        print(f"Erreur lors du traitement : {e}")

if __name__ == "__main__":
    # On suppose que le script est lancé depuis le dossier sources ou que assets.jpeg est accessible
    # Si lancé depuis la racine du projet, il faudra peut-être ajuster le chemin
    
    target_file = "assets.jpeg"
    
    # Petit check pour voir si on est dans sources ou à la racine
    if not os.path.exists(target_file) and os.path.exists(os.path.join("sources", target_file)):
        target_file = os.path.join("sources", target_file)
        
    process_assets(target_file, target_file.replace(".jpeg", "_no_bg.png").replace(".jpg", "_no_bg.png"))
