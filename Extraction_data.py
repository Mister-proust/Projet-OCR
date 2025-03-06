import requests
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

load_dotenv()
url_serv = os.getenv("URL_SERVEUR")
sas_serv = os.getenv("SAS_SERVEUR")


for i in range(2018, 2025):
    url = url_serv + str(i) + "?restype=container&comp=list&" + sas_serv

    response = requests.get(url)

    root = ET.fromstring(response.content)

    os.makedirs(f"data/factures/{i}", exist_ok=True)

    for Blob in root.findall(".//Blob"):     
        name = Blob.find("Name").text

        print("Facture :", name)
        new_url = url_serv + str(i) + "/"+ str(name) + "?" + sas_serv
        facture_path = f"data/factures/{i}/{name}"
        download_png = requests.get(new_url)
        with open(facture_path, 'wb') as f:
                f.write(download_png.content)
        print("Facture téléchargée")



