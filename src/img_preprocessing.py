from PIL import Image
from pathlib import Path
import numpy as np
from lib.feature_extractor import FeatureExtractor

if __name__ == "__main__":
    fe = FeatureExtractor()
    
    for img_path in sorted(Path("src/static/dataset").glob("*.jpg")):
        # Extract feature
        feature = fe.extract(img=Image.open(img_path))
        feature_path = Path("src/static/feature") / (img_path.stem + "_hsv" + ".npy")
        
        # Save feature
        np.save(feature_path, feature)
    