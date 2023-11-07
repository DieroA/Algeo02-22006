from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
from PIL import Image
import io
import os

# IMAGE SCRAPPING DARI GOOGLE IMAGES

# TAMBAH: pencet "Show more results", stop kalo ketemu "Looks like you've reached the end"

def scroll(wd):
# Scroll ke paling bawah
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

def cari_url(topik, MAX_URL, wd):
# Mengembalikan URL gambar dari google images
    # Search { topik } di Google
    url_cari = f"https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={topik}&oq={topik}&gs_l=img"
    wd.get(url_cari)

    url_gambar = set()
    while (len(url_gambar) < MAX_URL):
        scroll(wd)

        thumbnails = wd.find_elements(By.CSS_SELECTOR, "img.Q4LuWd")

        for img in thumbnails[len(url_gambar) : len(thumbnails)]:
            try:
                img.click()
                time.sleep(2)
            except:
                continue
            
            images = wd.find_elements(By.CSS_SELECTOR, ".sFlh5c.pT0Scc.iPVvYb")
            for image in images:
                if (image.get_attribute("src") and "http" in image.get_attribute("src")):
                    url_gambar.add(image.get_attribute("src"))  # Add ke url_gambar kalo src image mengandung link
    return url_gambar

def download_url(folder_path, url, name):
# Mendownload file yang terdapat pada { url } ke { folder_path } dengan nama file { name }
    path = folder_path + name

    try:
        img_binary = requests.get(url).content
        img_file = io.BytesIO(img_binary)
        img = Image.open(img_file)

        img.save(open(path, "wb"), "JPEG")
    except:
        pass

def udah_ada(folder_path, file_name):
# Cek apakah { file_name } sudah ada dalam folder { folder_path } atau belum
    file_path = os.path.join(folder_path, file_name)
    return (os.path.isfile(file_path))

# Main
wd = webdriver.Chrome()
urls = cari_url("Cat", 5, wd)
n = 0
for i in urls:

    # Ganti nama file jika file dengan nama { name } sudah ada dalam folder dataset
    name = "test" + str(n) + ".jpg"
    while (udah_ada("src/static/dataset", name)):
        n += 1
        name = "test" + str(n) + ".jpg"

    download_url("src/static/dataset/", i, name)
    n += 1
wd.quit()