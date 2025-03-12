from Test_OCR.tesseract_ocr import resize_image, mask_qr_code, mask_photo, grayscale, thresholding, draw_bounding_boxes
import pytest
import cv2

def test_tesseract() : 
    input_path = "data/test/test.png"
    output_path = "data/test.png"
    img = cv2.imread(input_path)
    resized_img = resize_image(img, scale=2) 
    masked_img = mask_qr_code(resized_img)  
    masked_img = mask_photo(masked_img)      
    gray = grayscale(masked_img)            
    thresh = thresholding(gray)              
    text = draw_bounding_boxes(thresh, output_path)
    print(f"le texte est le suivant : {text}")
    assert "TEST 2025" == text.strip()