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
page = 0
img_name = ""
parent_dir = ""
end, start = 0, 0

@app.route("/program", methods=["GET", "POST"])
def index():
    global scores, pagination, page, img_name, parent_dir, end, start
    if request.method == "POST":
        dataset = request.files.getlist("folder_dataset")
        query = request.files["query_img"]
        
        page = 1
        dir_name = 'src/static/dataset/'

        no_data_input = not dataset[0]
        no_query_input = not query
        start = time.time()
        if no_data_input and not os.listdir(dir_name):
            return render_template("index.html", error_dataset_empty=no_data_input)
        else:
            if not no_data_input:
                # Save dataset images and delete previous dataset and features
                parent_dir = os.path.basename(os.path.dirname(dataset[0].filename))
                uploaded_dataset_path = "src/static/dataset/" + parent_dir
                if (os.listdir(dir_name)):
                    shutil.rmtree(dir_name)
                textures = [feature for feature in os.listdir("src/static/feature/texture")]
                for feature in textures:
                    os.remove(os.path.join("src/static/feature/texture", feature))
                colors = [feature for feature in os.listdir("src/static/feature/hsv")]
                for feature in colors:
                    os.remove(os.path.join("src/static/feature/hsv", feature))

                os.makedirs(dir_name + parent_dir, exist_ok=True)
                for images in dataset:
                    img = Image.open(images.stream)
                    img.save(dir_name + images.filename)
                
                # Extract features from dataset
                allowed_extensions = ['.jpg', '.jpeg', '.png']
                for img_path in sorted(Path("src/static/dataset/" + parent_dir).glob("*")):
                    if img_path.suffix.lower() in allowed_extensions:
                        print(img_path)
                        feature = fe.extractTexture(img=Image.open(img_path))
                        feature_path = Path("src/static/feature/texture") / (img_path.stem + "_texture" + ".npy") 
                        np.save(feature_path, feature)
                
                for img_path in sorted(Path("src/static/dataset/" + parent_dir).glob("*")):
                    if img_path.suffix.lower() in allowed_extensions:
                        print(img_path)
                        feature = fe.extractHSV(img=Image.open(img_path))
                        feature_path = Path("src/static/feature/hsv") / (img_path.stem + "_hsv" + ".npy") 
                        np.save(feature_path, feature)
            else:
                parent_dir = os.listdir(dir_name)[0]

        if no_query_input:
            return render_template("index.html", error_query_empty=no_query_input)

        # Save query image
        img = Image.open(query.stream)
        uploaded_img_path = "src/static/query/"
        img_name = datetime.now().isoformat().replace(":",".") + "_" + query.filename
        img.save(uploaded_img_path + img_name)
        
        # Run search on database
        img_paths = []
        for img_path in Path("src/static/dataset/" + parent_dir).glob("*"):
            img_paths.append(img_path.stem + img_path.suffix.lower())
            
        if request.form.get("cbir-by-texture"):
            features_texture = []
            for feature_path in Path("src/static/feature/texture").glob("*.npy"):
                features_texture.append(np.load(feature_path))
            features_texture = np.array(features_texture)
            
            img = Image.open("src/static/query/" + img_name)
            query = fe.extractTexture(img)
            dists = np.empty([len(features_texture)])
            for i in range(len(features_texture)):
                if (np.isnan(cbc.cosine_similarity(query, features_texture[i]))):
                    dists[i] = 0
                else:
                    dists[i] = cbc.cosine_similarity(query, features_texture[i])
        else:
            features_hsv = []
            for feature_path in Path("src/static/feature/hsv").glob("*.npy"):
                features_hsv.append(np.load(feature_path))
            features_hsv = np.array(features_hsv)

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
        if not page:
            page = int(request.args.get('page', 1))    
        per_page = 20
        items = paginate(page, per_page, scores)
        total_items = len(scores)
        total_pages = (total_items - 1) // per_page + 1
        
        print(page, per_page, items, total_items, total_pages)
        
        return render_template("index.html", query_path=img_name, scores=items, dataset_folder=parent_dir, time=round(end-start, 2), img_count=total_items,
                               pagination = {'current_page' : page, 'per_page' : per_page, 'total_pages' : total_pages, 'total_items' : total_items})
    else:
        page = int(request.args.get('page', 1))
        per_page = 20
        items = paginate(page, per_page, scores)
        total_items = len(scores)
        total_pages = (total_items - 1) // per_page + 1
        
        return render_template("index.html", query_path=img_name, scores=items, dataset_folder=parent_dir, time=round(end-start, 2), img_count=total_items,
                               pagination = {'current_page' : page, 'per_page' : per_page, 'total_pages' : total_pages, 'total_items' : total_items})
    
def paginate(page, per_page, data):
    start = (page-1) * per_page
    end = start + per_page
    return data[start:end]

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/about-us", methods=["GET"])
def about_us():
    return render_template("about-us.html")

if __name__ == "__main__":
    app.run(debug="True")