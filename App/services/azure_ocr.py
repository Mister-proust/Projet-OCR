import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import cv2
import matplotlib.pyplot as plt
import requests
import xml.etree.ElementTree as ET
import glob 


load_dotenv()
endpoint = os.getenv("VISION_ENDPOINT")
key = os.getenv("VISION_KEY")
url_serv = os.getenv("URL_SERVEUR")
sas_serv = os.getenv("SAS_SERVEUR")



def get_words() : 
    UPLOAD_DIR = "./static/uploads/"
    images = glob.glob(os.path.join(UPLOAD_DIR, "image_telecharge.*"))

    if not images:
        return "Aucune image trouvée", None

    image_path = images[0]
    image_ext = os.path.splitext(image_path)[1] 

    with open(image_path, "rb") as image_file:
        file_bytes = image_file.read()


    client = ImageAnalysisClient(endpoint, AzureKeyCredential(key)) 
    result = client.analyze(image_data=file_bytes, visual_features=[VisualFeatures.READ])

    image2 = cv2.imread(image_path)

    for block in result.read.blocks : 
        for line in block.lines : 
            line_box = line['boundingPolygon']
            top_left = (line_box[0]['x'], line_box[0]['y'])
            bottom_right = (line_box[2]['x'], line_box[2]['y'])
            cv2.rectangle(image2, top_left, bottom_right, (0,255,0), 2)

            for word in line.words :
                word_box = word['boundingPolygon']
                top_left = (word_box[0]['x'], word_box[0]['y'])
                bottom_right = (word_box[2]['x'], word_box[2]['y'])
                cv2.rectangle(image2, top_left, bottom_right, (0,0,255), 1)
                

    
    OUTPUT_DIR = "./static/uploads/"
    image_enregistree = os.path.join(OUTPUT_DIR, f"image_vert{image_ext}")
    cv2.imwrite(image_enregistree, image2)
    cv2.destroyAllWindows()

    return  result, image_enregistree

if __name__ == "__main__" : 
    get_words()