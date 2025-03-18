from pyzbar.pyzbar import decode
from PIL import Image
import re
import os
import glob

# Fonction qui récupère les fichiers d'invoice
def get_invoice_files(base_path="data/factures"):
    invoice_files = []
    for year in range(2018, 2026):  # Exemple pour 2018
        year_path = os.path.join(base_path, str(year))
        files = glob.glob(os.path.join(year_path, "*.png")) + glob.glob(os.path.join(year_path, "*.jpg"))
        invoice_files.extend(files)
    
    return invoice_files

# Fonction qui extrait les données du QR code
def extract_qr_data(invoice_path):
    x = decode(Image.open(invoice_path))

    if not x:
        print(f"⚠️ Aucun QR code trouvé dans l'image : {invoice_path}")
        return None

    regex = x[0].data.decode('utf-8')

    # Extraction des données via des expressions régulières
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

# Fonction pour traiter toutes les factures
def process_invoices():
    invoice_files = get_invoice_files()  # Récupérer les fichiers
    for invoice_path in invoice_files:
        print(f"📄 Traitement de : {invoice_path}")
        
        # Extraire les données du QR code
        qr_data = extract_qr_data(invoice_path)

        if qr_data:
            print(f"QR Data : {qr_data}")
        else:
            print("Aucun QR code trouvé pour cette facture.")

# Appel de la fonction principale
if __name__ == "__main__":
    process_invoices()
