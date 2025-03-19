from Database.db_connection import build_engine, build_dburl
from Database.models.table_database import Utilisateur, Facture, Article
from Database.db_connection import SQLClient
from Test_OCR.tesseract_ocr import get_invoice_files, resize_image, mask_photo, grayscale, thresholding, draw_bounding_boxes
import cv2
from Test_OCR.qrcode_ocr import extract_qr_data

path = build_dburl

def create_tables():
    print("Création des tables...")
    engine, _ = build_engine()
    #Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès !")


def add_data(client, data, invoice_path):
    qr_data = extract_qr_data(invoice_path)
    
    if qr_data:
        print(f"📋 Données extraites du QR code : {qr_data}")

        if "nom_facture" in qr_data and qr_data["nom_facture"]:
            data["facture"]["nom_facture"] = qr_data["nom_facture"]
        if "date_facture" in qr_data and qr_data["date_facture"]:
            data["facture"]["date_facture"] = qr_data["date_facture"]
        if "genre" in qr_data and qr_data["genre"]:
            data["utilisateur"]["genre"] = qr_data["genre"]
        if "date_anniversaire" in qr_data and qr_data["date_anniversaire"]:
            data["utilisateur"]["date_anniversaire"] = qr_data["date_anniversaire"]

    img = cv2.imread(invoice_path)
    if img is None:
        print(f"Impossible de lire le fichier : {invoice_path}, veuillez réassayer")
        return

    resized_img = resize_image(img, scale=2)
    masked_img = mask_photo(resized_img)
    gray = grayscale(masked_img)
    thresh = thresholding(gray)

    ocr_data = draw_bounding_boxes(thresh, invoice_path.replace(".png", "_boxes.png"))
    
    # Données OCR avec QR code implémenté en même temps.
    for section in ["utilisateur", "facture"]:
        if section in ocr_data and section in data:
            for key, value in ocr_data[section].items():
                # Ne pas écraser les données du QR code si elles existent déjà
                if key not in data[section] or not data[section][key]:
                    data[section][key] = value
    
    if "articles" in ocr_data:
        data["articles"] = ocr_data["articles"]

    if data["facture"]["nom_facture"]:
        # Ajout des données dans la BDD
        add_data_to_db(client, data)
    else:
        print(f"⚠️ Aucune facture détectée dans : {invoice_path}")

def add_data_to_db(client, data):
    # Onglet utilisateur
    utilisateur = Utilisateur(**data["utilisateur"])
    client.insert(utilisateur)

    # Onglet facture
    facture = Facture(**data["facture"])
    client.insert(facture)

    # Onglet article
    for article_data in data["articles"]:
        article = Article(**article_data)
        client.insert(article)

    print(f"Donnée de la facture ajoutée avec succès (nom de la facture : {data['facture']['nom_facture']})")

if __name__ == "__main__":
    client = SQLClient()
    invoice_files = get_invoice_files()

    for invoice_path in invoice_files:
        print(f"Traitement de : {invoice_path}")

        data = {
            "utilisateur": {},
            "facture": {},
            "articles": []
        }
        
        add_data(client, data, invoice_path)

    print("Toutes les factures ont été traitées et insérées dans la BDD !")