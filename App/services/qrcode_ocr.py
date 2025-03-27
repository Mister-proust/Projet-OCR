from pyzbar.pyzbar import decode
from PIL import Image
import re
import os
import glob

UPLOAD_DIR = "./static/uploads/"

def get_invoice_files():
    images = glob.glob(os.path.join(UPLOAD_DIR, "image_telecharge.*"))  
    if not images:
        return "Aucune image trouvée", None  
    return images[0]

def extract_qr_data(image_path):
    x = decode(Image.open(image_path))

    if not x:
        print(f"Aucun QR code trouvé: {image_path}, Veuillez réassayer")
        return None

    regex = x[0].data.decode('utf-8')

    nom_facture = re.findall(r'FAC/\d{4}/\d+', regex)
    date_facture = re.findall(r'DATE:(\d{4}-\d{2}-\d{2})', regex)
    genre = re.findall(r'CUST:(\w)', regex)
    date_anniversaire = re.findall(r'birth (\d{4}-\d{2}-\d{2})', regex)

    return {
        "nom_facture": nom_facture[0] if nom_facture else None,
        "date_facture": date_facture[0] if date_facture else None,
        "genre": genre[0] if genre else None,
        "date_anniversaire": date_anniversaire[0] if date_anniversaire else None
    }
