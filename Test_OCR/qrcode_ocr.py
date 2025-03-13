from pyzbar.pyzbar import decode
from PIL import Image
import re

x=decode(Image.open('../data/factures/2018/FAC_2018_0036-284.png'))

regex = x[0].data.decode('utf-8')
print(regex)

nom_facture = re.findall(r'FAC/\d{4}/\d+', regex)
date_facture = re.findall(r'DATE:(\d{4}-\d{2}-\d{2})', regex)
gender = re.findall(r'CUST:(\w)', regex)
date_anniversaire = re.findall(r'birth (\d{4}-\d{2}-\d{2})', regex)


print(nom_facture)
print(date_facture)
print(gender)
print(date_anniversaire)