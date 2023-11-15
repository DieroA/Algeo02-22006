import numpy as np
import lib.cbir_by_color as cbc
import lib.cbir_by_tekstur as cbt
import time
import os
import shutil
from PIL import Image
from lib.feature_extractor import FeatureExtractor
from datetime import datetime
from flask import Flask, request, render_template
from pathlib import Path

app = Flask(__name__)
fe = FeatureExtractor()

scores = []
pagination = {}
img_name = ""
parent_dir = ""
end, start = 0, 0

@app.route("/", methods=["GET", "POST"])
def index():
    global scores, pagination, img_name, parent_dir, end, start
    if request.method == "POST":
        dataset = request.files.getlist("folder_dataset")
        query = request.files["query_img"]
        
        no_data_input = not dataset[0]
        no_query_input = not query
        if no_data_input or no_query_input:
            return render_template("index.html", error_dataset_empty=no_data_input, error_query_empty=no_query_input)
        
        # Delete previous dataset and features
        parent_dir = os.path.basename(os.path.dirname(dataset[0].filename))
        uploaded_dataset_path = "src/static/dataset/" + parent_dir
        if (os.path.isdir(uploaded_dataset_path)):
            shutil.rmtree(uploaded_dataset_path)
        textures = [feature for feature in os.listdir("src/static/feature/texture")]
        for feature in textures:
            os.remove(os.path.join("src/static/feature/texture", feature))
        colors = [feature for feature in os.listdir("src/static/feature/hsv")]
        for feature in colors:
            os.remove(os.path.join("src/static/feature/hsv", feature))
        
        # Save query and dataset images
        img = Image.open(query.stream)
        uploaded_img_path = "src/static/query/"
        img_name = datetime.now().isoformat().replace(":",".") + "_" + query.filename
        img.save(uploaded_img_path + img_name)
        
        os.makedirs(uploaded_dataset_path, exist_ok=True)
        uploaded_dataset_path = "src/static/dataset/"
        for images in dataset:
            img = Image.open(images.stream)
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
                elif cbt.Cosine_Similarity(query, features_texture[i]) >= 1:
                    dists[i] = 1
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
        
        # Paginate the result
        page = int(request.args.get('page', 1))
        per_page = 5
        items = paginate(page, per_page, scores)
        total_items = len(scores)
        total_pages = (total_items - 1) // per_page + 1
        
        print(page, per_page, items, total_items, total_pages)
        
        return render_template("index.html", query_path=img_name, scores=items, dataset_folder=parent_dir, time=end-start, img_count=total_items,
                               pagination = {'current_page' : page, 'per_page' : per_page, 'total_pages' : total_pages, 'total_items' : total_items})
    else:
        page = int(request.args.get('page', 1))
        per_page = 5
        items = paginate(page, per_page, scores)
        total_items = len(scores)
        total_pages = (total_items - 1) // per_page + 1
        
        return render_template("index.html", query_path=img_name, scores=items, dataset_folder=parent_dir, time=end-start, img_count=total_items,
                               pagination = {'current_page' : page, 'per_page' : per_page, 'total_pages' : total_pages, 'total_items' : total_items})
    
def paginate(page, per_page, data):
    start = (page-1) * per_page
    end = start + per_page
    return data[start:end]

@app.route("/home", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/about-us", methods=["GET"])
def about_us():
    return render_template("about-us.html")

if __name__ == "__main__":
    app.run(debug="True")