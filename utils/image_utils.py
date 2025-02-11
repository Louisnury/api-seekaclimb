import os
import uuid
from PIL import Image
import io

WALLS_DIR = "static/walls"

def save_wall_images(place_name, image_data, thumbnail_data):
    """
    Sauvegarde les images d'un mur et retourne le nom de fichier généré
    """
    # Création des dossiers nécessaires
    place_dir = os.path.join(WALLS_DIR, sanitize_filename(place_name))
    images_dir = os.path.join(place_dir, "images")
    thumbnails_dir = os.path.join(place_dir, "thumbnails")
    
    for directory in [place_dir, images_dir, thumbnails_dir]:
        os.makedirs(directory, exist_ok=True)
    
    # Génération d'un nom de fichier unique
    filename = f"{uuid.uuid4()}.jpg"
    
    # Sauvegarde de l'image principale
    image_path = os.path.join(images_dir, filename)
    image = Image.open(io.BytesIO(image_data))
    image.save(image_path, "JPEG")
    
    # Sauvegarde de la miniature
    thumbnail_path = os.path.join(thumbnails_dir, filename)
    thumbnail = Image.open(io.BytesIO(thumbnail_data))
    thumbnail.save(thumbnail_path, "JPEG")
    
    return filename

def sanitize_filename(filename):
    """
    Nettoie le nom de fichier pour qu'il soit valide
    """
    return "".join(c for c in filename if c.isalnum() or c in (' -_')).rstrip()
