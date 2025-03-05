import requests
import xml.etree.ElementTree as ET
import os



for i in range(2018, 2026):
    url = "https://projetocrstorageacc.blob.core.windows.net/invoices-" + str(i) + "?restype=container&comp=list&sv=2019-12-12&ss=b&srt=sco&sp=rl&se=2026-01-01T00:00:00Z&st=2025-01-01T00:00:00Z&spr=https&sig=%2BjCi7n8g%2F3849Rprey27XzHMoZN9zdVfDw6CifS6Y1U%3D"

    response = requests.get(url)

    root = ET.fromstring(response.content)

    os.makedirs(f"data/factures/{i}", exist_ok=True)

    for Blob in root.findall(".//Blob"):     
        name = Blob.find("Name").text

        print("Facture :", name)
        new_url = "https://projetocrstorageacc.blob.core.windows.net/invoices-" + str(i) + "/"+ str(name) + "?sv=2019-12-12&ss=b&srt=sco&sp=rl&se=2026-01-01T00:00:00Z&st=2025-01-01T00:00:00Z&spr=https&sig=%2BjCi7n8g%2F3849Rprey27XzHMoZN9zdVfDw6CifS6Y1U%3D"
        facture_path = f"data/factures/{i}/{name}"
        download_png = requests.get(new_url)
        with open(facture_path, 'wb') as f:
                f.write(download_png.content)
        print("Facture téléchargée")



