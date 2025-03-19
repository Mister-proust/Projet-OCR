import cv2
import pytesseract
from pytesseract import Output
import matplotlib.pyplot as plt
import re

input_path = "../data/factures/2024/FAC_2024_0378-191.png"
output_path = "../data/FAC_2024_0378-284_boxes.png"


def resize_image(image, scale=3):
    height, width = image.shape[:2]
    new_size = (width * scale, height * scale)
    return cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)

def mask_photo(image):
    height, width = image.shape[:2]
    
    x_start = int(width * 0.55)  
    y_start = 0               
    x_end = width              
    y_end = int(height * 0.15) 
    
    cv2.rectangle(image, (x_start, y_start), (x_end, y_end), (255, 255, 255), -1)
    
    return image

def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def thresholding(image):
    _, binary = cv2.threshold(image, 240, 255, cv2.THRESH_BINARY)
    return binary

def draw_bounding_boxes(preprocessed_img, output_path):
    text = pytesseract.image_to_string(preprocessed_img, config='--psm 6')
    #print(text)
    nom_facture = re.findall(r'FAC/\d{4}/\d+', text)
    #print(nom_facture)
    date_facture = re.findall(r'date (\d{4}-\d{2}-\d{2})', text)
    #print(date_facture)
    nom_personne = re.findall(r'Bill to ([^\n]+)', text)
    #print(nom_personne)
    email_personne = re.findall(r'Email ([^\n]+)', text)
    #print(email_personne)
    rue_num_personne = re.findall(r'Address ([^\n]+)', text)
    #print(rue_num_personne)
    ville_personne = [v.strip() for v in re.findall(r'Address [^\n]+\n([\w\s-]+), \w{2} \d{5}', text)]
    #print(ville_personne)
    code_postal_personne = re.findall(r', (\w{2} \d{5})', text)
    #print(code_postal_personne)

    articles = re.findall(r'^(.*?)\s+\d+\s*x\s+[\d,.]+\s+Euro$', text, re.MULTILINE)
    article_vars = {f"article_{i+1}": article for i, article in enumerate(articles)}
    articles_list = list(article_vars.values())
    #print(articles_list) 

    quantite = re.findall(r'(\d+)\s*x\s*[\d,.]+\s+Euro', text)
    quantite = [int(q) for q in quantite]  
    #print("Quantités :", quantite)

    prix = re.findall(r'\d+\s*x\s*([\d,.]+)\s+Euro', text)
    prix = [float(p.replace(',', '.')) for p in prix] 
    #print("Prix :", prix)

    total = re.findall(r'TOTAL\s+([\d,.]+)\s+Euro', text)
    total = float(total[0].replace(',', '.')) if total else None
    #print("Montant total :", total)

    data = {
        "utilisateur": {
            "email_personne": email_personne[0] if email_personne else None,
            "nom_personne": nom_personne[0] if nom_personne else None,
            "genre": None,
            "rue_num_personne": rue_num_personne[0] if rue_num_personne else None,
            "ville_personne": ville_personne[0] if ville_personne else None,
            "code_postal_personne": code_postal_personne[0] if code_postal_personne else None,
            "date_anniversaire": None,
        },
        "facture": {
            "nom_facture": nom_facture[0] if nom_facture else None,
            "date_facture": date_facture[0] if date_facture else None,
            "total_facture": total,
            "email_personne": email_personne[0] if email_personne else None,
        },
        "articles": [
            {
                "nom_facture": nom_facture[0] if nom_facture else None,
                "nom_article": articles[i] if i < len(articles) else None,
                "quantite": quantite[i] if i < len(quantite) else None,
                "prix": prix[i] if i < len(prix) else None,
            }
            for i in range(len(articles))
        ],
    }

    # Le code suivant permet d'encadrer en vert les zones repérées ainsi que d'enregistrer le fichier.
    """
    data = pytesseract.image_to_data(preprocessed_img, output_type=Output.DICT)
    n_boxes = len(data["text"])

    for i in range(n_boxes):
        if data["text"][i].strip():  
            x, y = data["left"][i], data["top"][i]
            w, h = data["width"][i], data["height"][i]
            cv2.rectangle(preprocessed_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imwrite(output_path, preprocessed_img)
    """
    return data

import os
import glob

def get_invoice_files(base_path="data/factures"):
    invoice_files = []
    for year in range(2018, 2026):  
        year_path = os.path.join(base_path, str(year))  
        files = glob.glob(os.path.join(year_path, "*.png")) + glob.glob(os.path.join(year_path, "*.jpg"))
        invoice_files.extend(files)
    
    return invoice_files

invoice_files = get_invoice_files()

for invoice_path in invoice_files:
    print(f"Traitement de : {invoice_path}")

    img = cv2.imread(invoice_path)  
    if img is None:
        print(f"Impossible de lire l'image : {invoice_path}, Veuillez réassayer")
        continue

    resized_img = resize_image(img, scale=2) 
    masked_img = mask_photo(resized_img)      
    gray = grayscale(masked_img)            
    thresh = thresholding(gray)              

    text = draw_bounding_boxes(thresh, invoice_path.replace(".png", "_boxes.png"))  
    #print(f"Texte extrait : {text}")

if __name__ == "__main__":
    img = cv2.imread(input_path)
    resized_img = resize_image(img, scale=2) 
    masked_img = mask_photo(resized_img)      
    gray = grayscale(masked_img)            
    thresh = thresholding(gray)              
    draw_bounding_boxes(thresh, output_path) 
    get_invoice_files(base_path="../data/factures")

