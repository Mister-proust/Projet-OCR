from doctr.models import ocr_predictor
from doctr.io import DocumentFile
import json

model = ocr_predictor(det_arch='db_resnet50', reco_arch='sar_resnet31', pretrained=True)
# Load an image
image_path = DocumentFile.from_images('../data/factures/2018/FAC_2018_0036-284.png')

# Perform OCR on the image
result = model(image_path)

result_json= result.export()
print(json.dumps(result_json, indent=4))

result.show()

