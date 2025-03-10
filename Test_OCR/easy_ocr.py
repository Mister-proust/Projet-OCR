### Manque beaucoup d'informations.

import easyocr
import cv2
import matplotlib.pyplot as plt

image = "../data/factures/2018/FAC_2018_0036-284.png"

# Create an OCR reader object
reader = easyocr.Reader(['en'])


# Read text from an image
result = reader.readtext(image, width_ths=2, )
print(result)

image2 = cv2.imread(image)
for detection in result:
    top_left = tuple([int(val) for val in detection[0][0]])
    bottom_right = tuple([int(val) for val in detection[0][2]])
    text = detection[1]
    font = cv2.FONT_HERSHEY_SIMPLEX
    image2 = cv2.rectangle(image2, top_left, bottom_right, (0,255,0), 2)
    image2 = cv2.putText(image2, text, top_left, font, 0.5, (255,255,255), 1, cv2.LINE_AA)

plt.figure(figsize=(10,10))
plt.imshow(image2)
plt.show()
