from pyzbar.pyzbar import decode
from PIL import Image

x=decode(Image.open('../data/factures/2018/FAC_2018_0036-284.png'))

print(x[0].data.decode('utf-8'))