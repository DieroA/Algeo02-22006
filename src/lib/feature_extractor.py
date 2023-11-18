import numpy as np
import lib.cbir_by_color as cbc
import lib.cbir_by_tekstur as cbt
from PIL import Image
from pathlib import Path

class FeatureExtractor:
    def __init__(self):
        pass
    
    def extractHSV(self, img):
        img = img.resize((256, 256)).convert("RGB")
        hsv = cbc.to_hsv(np.array(img))
        res = cbc.to_histogram(hsv, np.empty([64, 64, 3], dtype=np.float64))

        return res
    
    def extractTexture(self, img):
        img = img.resize((256, 256))
        vector = cbt.Hasil_CBIR_Tekstur(np.array(img))
        
        return vector
    
# fe = FeatureExtractor()
# img1 = Image.open("src/static/query/2023-11-12T15.07.16.275630_Red_Color.jpg")
# img2 = Image.open("src/static/query/2023-11-05T21.07.09.491461_Official_portrait_of_Barack_Obama.jpg")
# arr1 = fe.extractTexture(img1)
# arr2 = fe.extractTexture(img2)
# arr1 = np.array(arr1)
# arr2 = np.array(arr2)

# print(arr1.shape, arr2.shape, arr1, arr2)
# dist = cbt.Cosine_Similarity(arr1, arr2)
# print("dist", dist)