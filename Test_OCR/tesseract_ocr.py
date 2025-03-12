import cv2
import pytesseract
from pytesseract import Output
import matplotlib.pyplot as plt

input_path = "../data/factures/2018/FAC_2018_0002-114.png"
output_path = "../data/FAC_2018_0036-284_boxes.png"


def resize_image(image, scale=2):
    height, width = image.shape[:2]
    new_size = (width * scale, height * scale)
    return cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)

def mask_qr_code(image):
    qr_detector = cv2.QRCodeDetector()
    _, qr_bbox, _ = qr_detector.detectAndDecode(image)

    if qr_bbox is not None:
        qr_bbox = qr_bbox.astype(int)
        x, y, w, h = cv2.boundingRect(qr_bbox)
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), -1)
    
    return image

def mask_photo(image):
    height, width = image.shape[:2]
    
    x_start = int(width * 0.75)  
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
    print(text)

    data = pytesseract.image_to_data(preprocessed_img, output_type=Output.DICT)
    n_boxes = len(data["text"])

    for i in range(n_boxes):
        if data["text"][i].strip():  
            x, y = data["left"][i], data["top"][i]
            w, h = data["width"][i], data["height"][i]
            cv2.rectangle(preprocessed_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imwrite(output_path, preprocessed_img)
    return text

if __name__ == "__main__":
    img = cv2.imread(input_path)
    resized_img = resize_image(img, scale=2) 
    masked_img = mask_qr_code(resized_img)  
    masked_img = mask_photo(masked_img)      
    gray = grayscale(masked_img)            
    thresh = thresholding(gray)              
    draw_bounding_boxes(thresh, output_path) 
