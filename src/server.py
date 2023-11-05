import numpy as np
import lib.cbir_by_color as cbc
import time
from PIL import Image
from lib.feature_extractor import FeatureExtractor
from datetime import datetime
from flask import Flask, request, render_template
from pathlib import Path

app = Flask(__name__)

fe = FeatureExtractor()
features = []
img_paths = []

# Read img features
for feature_path in Path("src/static/feature").glob("*.npy"):
    features.append(np.load(feature_path))
    img_paths.append(feature_path.stem.replace("_hsv", "")+ ".jpg")
    
features = np.array(features)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if request.form.get("cbir-by-texture"):
            return "Coming soon!"
        
        file = request.files["query_img"]
        
        # Save query image
        img = Image.open(file.stream)
        uploaded_img_path = "src/static/query/"
        img_name = datetime.now().isoformat().replace(":",".") + "_" + file.filename
        
        img.save(uploaded_img_path + img_name)
        
        # Run search on database
        query = fe.extract(img)
        dists = np.empty([len(features)])
        
        start = time.time()
        for i in range(len(features)):
            if (np.isnan(cbc.similarity(query, features[i]))):
                dists[i] = 0
            else:
                dists[i] = cbc.similarity(query, features[i])
        
        index, = np.where(dists >= 0.6)
        ids = index[np.argsort(dists[index])[::-1]]
        scores = [(dists[id], img_paths[id]) for id in ids]
        
        end = time.time()
        return render_template("index.html", query_path=img_name, scores=scores, time=end-start, img_count=len(ids))
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(debug="True")