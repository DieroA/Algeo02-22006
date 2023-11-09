from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
from PIL import Image
import io
import os

# IMAGE SCRAPPING DARI GOOGLE IMAGES

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
                if (image.get_attribute("src") and "http" in image.get_attribute("src") and (len(url_gambar) < MAX_URL)):
                    url_gambar.add(image.get_attribute("src"))  # Add ke url_gambar kalo src image mengandung link
        
        
        # Pencet tombol "Show more images" 
        show_more = wd.find_element(By.CSS_SELECTOR, ".LZ4I") 
        if (show_more):
            try:
                show_more.click()
            except:
                pass
        
        # Stop kalo ketemu "Looks like you've reached the end" << BELUM BISA
        # end = wd.find_element(By.CSS_SELECTOR, ".OuJzKb.Yu2Dnd")
        # if (end):
        #     break
    return url_gambar

def download_url(folder_path, url, name):
# Mendownload file yang terdapat pada { url } ke { folder_path } dengan nama file { name }
    path = folder_path + name

    try:
        request = requests.get(url, timeout = 10)
        if (request.status_code == 200):             # Status_code 200 >> request berhasil
            img_binary = request.content
            if (len(img_binary) == 0):
                return False 
            
            img_file = io.BytesIO(img_binary)
            img = Image.open(img_file)
            img = img.convert("RGB") 
            img.save(open(path, "wb"), "JPEG")
            return True
        else:
            return False
    except requests.exceptions.Timeout as t:
        print("Timeout: ", t)
        return False
    except Exception as e:
        print("Exception: ", e)
        return False

def udah_ada(folder_path, file_name):
# Cek apakah { file_name } sudah ada dalam folder { folder_path } atau belum
    file_path = os.path.join(folder_path, file_name)
    return (os.path.isfile(file_path))

# Main
wd = webdriver.Chrome()
urls = cari_url("Cat", 100, wd) # Ganti "Cat" jadi topik yang ingin dicari
wd.quit()

n, cnt, gagal = 0, 0, 0
for url in urls:
    # Ganti nama file jika file dengan nama { name } sudah ada dalam folder dataset
    name = "test" + str(n) + ".jpg"
    while (udah_ada("src/static/dataset", name)):
        n += 1
        name = "test" + str(n) + ".jpg"

    if (download_url("src/static/dataset/", url, name)):
        cnt += 1
    else:
        gagal += 1
    n += 1
print(f"Berhasil men-download {cnt} gambar.")
print(f"Gagal men-download {gagal} gambar.")