from Database.db_connection import build_engine, build_dburl
from Database.models.table_database import Utilisateur, Facture, Article
from Database.db_connection import SQLClient
from Test_OCR.tesseract_ocr import get_invoice_files, resize_image, mask_photo, grayscale, thresholding, draw_bounding_boxes
import cv2
from Test_OCR.qrcode_ocr import extract_qr_data

path = build_dburl

"""
def generated_data(n=1):

    datas = []
    f=Faker()
    for _ in range(n):
        
        email = f.email()
        nom_facture = f.bothify(text = 'FAC/####/??')
        datas.append( {
            "utilisateur" : {
                "email_personne" : email,
                "nom_personne" : f.name(),
                "genre" : f.bothify(text = '?') ,
                "rue_num_personne" : f.street_address(),
                "ville_personne" : f.city() ,
                "code_postal_personne" : f.postalcode() ,
                "date_anniversaire"
            }, 
            "facture" : {
                "nom_facture" : nom_facture ,
                "date_facture" : f.date(),
                "total_facture" : f.pydecimal(left_digits=4, right_digits=2, positive=True, min_value=1, max_value=1000),
                "email_personne" : email,

            },
            "article" : {
                "nom_facture"  : nom_facture ,
                "nom_article" : f.bothify(text = 'article ????????????????????????') ,
                "quantite" : int(f.bothify(text = '#')) ,
                "prix" : float(f.bothify(text = '##.##')) ,

            }
        })
    return datas
"""
def create_tables():
    print("Création des tables...")
    engine, _ = build_engine()
    #Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès !")

"""def add_data(client, data ):

    #Onglet utilisateur
    utilisateur = Utilisateur(**data["utilisateur"])
    client.insert(utilisateur)

    #Onglet facture
    facture = Facture(**data["facture"])
    client.insert(facture)

    #Onglet article
    if "articles" in data:
            for article_data in data["articles"]:
                article = Article(**article_data)  # Passe un dictionnaire de chaque article
                client.insert(article)
    else:
        print(f"⚠️ Aucun article trouvé pour la facture : {data['facture']['nom_facture']}")

    print(f"Donnée de la facture ajoutée avec succès (nom de la facture : {data['facture']['nom_facture']})")
"""

def add_data(client, data, invoice_path):
    # Extraire le QR code de l'image brute avant tout traitement
    qr_data = extract_qr_data(invoice_path)
    
    # Si les données QR code sont présentes, les intégrer à la structure data
    if qr_data:
        print(f"📋 Données extraites du QR code : {qr_data}")

        # Ajouter ou mettre à jour les informations du QR code
        if "nom_facture" in qr_data and qr_data["nom_facture"]:
            data["facture"]["nom_facture"] = qr_data["nom_facture"]
            print(f"🔑 Mise à jour du nom de la facture : {qr_data['nom_facture']}")
        if "date_facture" in qr_data and qr_data["date_facture"]:
            data["facture"]["date_facture"] = qr_data["date_facture"]
            print(f"🔑 Mise à jour de la date de la facture : {qr_data['date_facture']}")
        if "genre" in qr_data and qr_data["genre"]:
            data["utilisateur"]["genre"] = qr_data["genre"]
            print(f"🔑 Mise à jour du genre de l'utilisateur : {qr_data['genre']}")
        if "date_anniversaire" in qr_data and qr_data["date_anniversaire"]:
            data["utilisateur"]["date_anniversaire"] = qr_data["date_anniversaire"]
            print(f"🔑 Mise à jour de la date d'anniversaire : {qr_data['date_anniversaire']}")

    # Traitement de l'image pour la reconnaissance de la facture avec OCR
    img = cv2.imread(invoice_path)
    if img is None:
        print(f"⚠️ Impossible de lire l'image : {invoice_path}")
        return

    # Appliquer les transformations après l'extraction du QR code
    resized_img = resize_image(img, scale=2)
    masked_img = mask_photo(resized_img)
    gray = grayscale(masked_img)
    thresh = thresholding(gray)

    # Récupérer les données OCR et les fusionner avec les données existantes
    ocr_data = draw_bounding_boxes(thresh, invoice_path.replace(".png", "_boxes.png"))
    
    # Fusionner les données OCR avec les données existantes (incluant QR)
    # Seulement mettre à jour les valeurs non présentes ou vides
    for section in ["utilisateur", "facture"]:
        if section in ocr_data and section in data:
            for key, value in ocr_data[section].items():
                # Ne pas écraser les données du QR code si elles existent déjà
                if key not in data[section] or not data[section][key]:
                    data[section][key] = value
    
    # Pour les articles, on utilise ceux détectés par OCR
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

"""
# Menu principal
if __name__ == "__main__":
    client = SQLClient()
    client.drop_all()

    #datas =generated_data(10)
    #for data in datas : add_data(client, data)
        # Récupération des factures
    invoice_files = get_invoice_files()
   
    for invoice_path in invoice_files:
        print(f"📄 Traitement de : {invoice_path}")
        img = cv2.imread(invoice_path)
        if img is None:
            print(f"⚠️ Impossible de lire l'image : {invoice_path}")
            continue

        resized_img = resize_image(img, scale=2)
        masked_img = mask_photo(resized_img)
        gray = grayscale(masked_img)
        thresh = thresholding(gray)

        data = draw_bounding_boxes(thresh, invoice_path.replace(".png", "_boxes.png"))
        
        if data["facture"]["nom_facture"]:
            add_data(client, data)
        else:
            print(f"⚠️ Aucune facture détectée dans : {invoice_path}")

    print("🚀 Toutes les factures ont été traitées et insérées dans la BDD !")"""

if __name__ == "__main__":
    client = SQLClient()

    # Récupération des factures
    invoice_files = get_invoice_files()

    for invoice_path in invoice_files:
        print(f"📄 Traitement de : {invoice_path}")

        # Initialiser une structure de données vide
        data = {
            "utilisateur": {},
            "facture": {},
            "articles": []
        }
        
        # Appeler add_data en passant les données vides et le chemin de la facture
        add_data(client, data, invoice_path)

    print("🚀 Toutes les factures ont été traitées et insérées dans la BDD !")