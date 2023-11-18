# Deskripsi: Fungsi-fungsi untuk melakukan teknik CBIR dengan parameter tekstur
#            memanfaatkan contrast, homogeneity, dan entropy
from numba import njit
import numpy as np
import math

@njit
def Penjumlahan_Matriks(Matriks1, Matriks2):
# mengembalikan hasil penjumlahan 2 buah matriks
    return np.add(Matriks1, Matriks2)

@njit
def Transpose(Matriks):
# mengembalikan transpose dari matriks
    return np.transpose(Matriks)

@njit
def RGB_to_GrayScale_Formula(R, G, B):
# fungsi untuk mengubah RGB menjadi GrayScale
# y = 0.299R + 0.587G + 0.114B
    return 0.29*R + 0.587*G + 0.114*B

@njit
def Matriks_RGB_to_GrayScale(Mat_RGB):
# Mengubah matriks RGB menjadi matriks GrayScale
    # Mendapatkan jumlah baris dan kolom dari matriks
    height, width, = (Mat_RGB.shape)[0], (Mat_RGB.shape)[1]
    # print("height\n", height, "width\n", width)
    # Membuat matriks kosong dengan ukuran yang sama
    Matriks_GrayScale = np.empty((height, width))
    # Mengubah elemen matriks menjadi GrayScale
    for i in range(height):
        for j in range(width):
            Matriks_GrayScale[i,j] = round(RGB_to_GrayScale_Formula(Mat_RGB[i, j, 0], Mat_RGB[i, j, 1], Mat_RGB[i, j, 2]))
                                      # dilakukan pembulatan agar memudahkan pembuatan matriks Co-Occurence
    return Matriks_GrayScale

@njit
def Matriks_GrayScale_to_Co_Occurence(Mat_GrayScale):
# Mengubah matriks GrayScale menjadi matriks Co-Occurence
# menggunakan jarak 1 pixel dengan sudut 0 derajat
    # Mendapatkan jumlah baris dan kolom dari matriks
    height, width = (Mat_GrayScale.shape)[0], (Mat_GrayScale.shape)[1]

    # Membuat matriks kosong dengan ukuran 256x256 (dimensi GrayScale 0-255)
    Matriks_Co_Occurence = np.zeros((256, 256))

    for i in range(height):
        for j in range(width-1):
            baris = Mat_GrayScale[i][j]
            kolom = Mat_GrayScale[i][j+1]
            Matriks_Co_Occurence[int(baris)][int(kolom)] += 1
    
    return Matriks_Co_Occurence

@njit
def Matrix_Normalisation(Matriks):
# menormalisasi matriks
    sum = np.sum(Matriks)       # Menghitung jumlah seluruh elemen matriks
    Matriks /= sum              # Membagi setiap elemen matriks dengan jumlah seluruh elemen matriks
    return Matriks

@njit
def Texture_of_Image(Matriks):
# mengembalikan texture sebuah matriks co-occurence yang telah dinormalisasi
# contrast = sigma (P(i,j) * (i-j)^2)
# homogeneity = sigma (P(i,j) / (1 + (i-j)^2))
# entropy = -sigma ((P(i,j) * log(P(i,j))))
    # bonus
# dissimilarity = sigma (P(i,j) * |i-j|)
# ASM = sigma (P(i,j)^2)                            ASM = angular second moment
# energy = sqrt(ASM)
    Vektor = np.zeros((6))

    for i in range(256):
        for j in range(256):
            Vektor[0] += Matriks[i][j] * (pow(i-j, 2))                  # Vektor[0] = Contrast
            Vektor[1] += Matriks[i][j] / (1 + (pow(i-j, 2)))            # Vektor[1] = Homogeneity
            
            if Matriks[i][j] != 0:      # menghindari log(0) 
                Vektor[2] += Matriks[i][j] * math.log(Matriks[i][j])    # Vektor[2] = Entropy
            
            Vektor[3] += Matriks[i][j] * abs(i-j)                       # Vektor[3] = Dissimilarity
            Vektor[4] += pow(Matriks[i][j], 2)                          # Vektor[4] = ASM

    Vektor[2] *= -1
    Vektor[5] = math.sqrt(Vektor[4])                                    # Vektor[5] = Energy

    return Vektor

def Norm_Vektor(Vektor):
# mengembalikan nilai norm/magnitude (panjang) sebuah vektor
    magnitude = np.sum(np.power(Vektor, 2))     # setiap elemen dikuadratkan kemudian dijumlahkan
    return math.sqrt(magnitude)

@njit
def Cosine_Similarity(Vektor1, Vektor2):
# mengembalikan nilai cosine similarity dari 2 buah vektor
    vektor = np.multiply(Vektor1, Vektor2)      # mengalikan setiap elemen vektor yang bersesuaian
    sum = np.sum(vektor)                        # menjumlahkan setiap elemen vektor yang telah dikalikan
    
    return sum / (Norm_Vektor(Vektor1) * Norm_Vektor(Vektor2))

@njit
def Hasil_CBIR_Tekstur(matriks):
# mengembalikan hasil CBIR Tekstur dari gambar yang diinputkan
    matriks = Matriks_RGB_to_GrayScale(matriks)                     # Mengubah matriks RGB menjadi matriks GrayScale
    matriks = Matriks_GrayScale_to_Co_Occurence(matriks)            # Mengubah matriks GrayScale menjadi matriks Co-Occurence dengan jarak 1 pixel dan sudut 0 derajat
    matriks = Penjumlahan_Matriks(matriks, Transpose(matriks))      # Menjumlahkan matriks Co-Occurence dengan transpose-nya untuk mendapatkan matriks simetri
    matriks = Matrix_Normalisation(matriks)                         # Menormalisasi matriks
    vektor_Texture = Texture_of_Image(matriks)          # Menghitung vektor Contrast, Homogeneity, dan Entropy, Dissimilarity, ASM, dan Energy
    
    return vektor_Texture