import numpy as np
import lib.cbir_by_color as cbc

class FeatureExtractor:
    def __init__(self):
        pass
    
    def extract(self, img):
        img = img.resize((255, 255)).convert("RGB")
        # print("awal")
        # print(np.array(img))
        arr = cbc.to_hsv(cbc.to_histogram(np.array(img)))
        # print("akhir")
        # print(arr)
        
        return arr
        