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

    return  result

if __name__ == "__main__" : 
    get_words()