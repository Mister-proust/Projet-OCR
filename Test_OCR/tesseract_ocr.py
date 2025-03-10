import cv2
import pytesseract
from pytesseract import Output
import matplotlib.pyplot as plt


input_path = "../data/factures/2018/FAC_2018_0002-114.png"
output_path = "../data/FAC_2018_0036-284_boxes.png"

def resize_image(image, scale=2):
    height, width = image.shape[:2]  # Récupère les dimensions originales
    new_size = (width * scale, height * scale)  # Nouvelle taille

    return cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)

# Utilisation
img = cv2.imread(input_path)
resized_img = resize_image(img, scale=2)

def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def thresholding(image):
    #return cv2.adaptiveThreshold(image, 255, 
    #                             cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
    #                             cv2.THRESH_BINARY, 11, 2)
    _, binary = cv2.threshold(image, 240, 255, cv2.THRESH_BINARY)
    return binary
def contrast_enhancement(image):
    return cv2.equalizeHist(image)

gray = grayscale(resized_img)
thresh = thresholding(gray)

def draw_bounding_boxes(preprocessed_img, output_path):

    text = pytesseract.image_to_string(preprocessed_img, config='--psm 6')
    print(text)

    data = pytesseract.image_to_data(preprocessed_img, output_type=Output.DICT)
    n_boxes = len(data["text"])

    for i in range(n_boxes):
        if data["text"][i].strip():  # Vérifier si le texte extrait n'est pas vide
            x, y = data["left"][i], data["top"][i]
            w, h = data["width"][i], data["height"][i]
            cv2.rectangle(preprocessed_img, (x, y), (x + w, y + h), (0, 255, 0), 2)


    cv2.imwrite(output_path, preprocessed_img)


if __name__ == "__main__":
    draw_bounding_boxes(thresh, output_path)
