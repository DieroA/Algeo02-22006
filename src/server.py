import numpy as np
import lib.cbir_by_color as cbc
import lib.cbir_by_tekstur as cbt
import time
import os
from PIL import Image
from lib.feature_extractor import FeatureExtractor
from datetime import datetime
from flask import Flask, request, render_template
from pathlib import Path

app = Flask(__name__)
fe = FeatureExtractor()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        dataset = request.files.getlist("folder_dataset")
        query = request.files["query_img"]
        
        # Save query and dataset images
        img = Image.open(query.stream)
        uploaded_img_path = "src/static/query/"
        img_name = datetime.now().isoformat().replace(":",".") + "_" + query.filename
        img.save(uploaded_img_path + img_name)
        
        uploaded_dataset_path = "src/static/dataset/"
        for images in dataset:
            img = Image.open(images.stream)
            parent_dir = os.path.basename(os.path.dirname(images.filename))
            print(parent_dir)
            os.makedirs(uploaded_dataset_path + parent_dir, exist_ok=True)
            img.save(uploaded_dataset_path + images.filename)
        
        features_hsv = []
        features_texture = []
        img_paths = []
        
        start = time.time()
        
        # Extract features from dataset
        if request.form.get("cbir-by-texture"):
            for img_path in sorted(Path("src/static/dataset/" + parent_dir).glob("*.jpg")):
                print(img_path)
                feature = fe.extractTexture(img=Image.open(img_path))
                feature_path = Path("src/static/feature/texture") / (img_path.stem + "_texture" + ".npy") 
                np.save(feature_path, feature)
            
            for feature_path in Path("src/static/feature/texture").glob("*.npy"):
                features_texture.append(np.load(feature_path))
                img_paths.append(feature_path.stem.replace("_texture", "")+ ".jpg")
            
            features_texture = np.array(features_texture)
        
        else:
            for img_path in sorted(Path("src/static/dataset/" + parent_dir).glob("*.jpg")):
                print(img_path)
                feature = fe.extractHSV(img=Image.open(img_path))
                feature_path = Path("src/static/feature/hsv") / (img_path.stem + "_hsv" + ".npy") 
                np.save(feature_path, feature)
            
            for feature_path in Path("src/static/feature/hsv").glob("*.npy"):
                features_hsv.append(np.load(feature_path))
                img_paths.append(feature_path.stem.replace("_hsv", "")+ ".jpg")
            
            features_hsv = np.array(features_hsv)
        
        # Run search on database
        if request.form.get("cbir-by-texture"):
            img = Image.open("src/static/query/" + img_name)
            query = fe.extractTexture(img)
            dists = np.empty([len(features_texture)])
            for i in range(len(features_texture)):
                if (np.isnan(cbt.Cosine_Similarity(query, features_texture[i]))):
                    dists[i] = 0
                else:
                    dists[i] = cbt.Cosine_Similarity(query, features_texture[i])
        else:
            img = Image.open("src/static/query/" + img_name)
            query = fe.extractHSV(img)
            dists = np.empty([len(features_hsv)])
            for i in range(len(features_hsv)):
                if (np.isnan(cbc.similarity(query, features_hsv[i]))):
                    dists[i] = 0
                else:
                    dists[i] = cbc.similarity(query, features_hsv[i])
        
        index, = np.where(dists >= 0.6)
        ids = index[np.argsort(dists[index])[::-1]]
        img_paths = np.array(img_paths)
        
        print(dists.shape, img_paths.shape, ids.shape)
        scores = [(dists[id], img_paths[id]) for id in ids]
        
        end = time.time()
        
        return render_template("index.html", query_path=img_name, scores=scores, dataset_folder=parent_dir, time=end-start, img_count=len(ids))
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(debug="True")