import numpy as np
import math

def rgb_to_hsv(R, G, B):
    r = R / 255
    g = G / 255
    b = B / 255
    
    cMax = max(r, g, b)
    cMin = min(r, g, b)
    delta = cMax - cMin
    
    # Compute h
    if delta == 0:
        h = 0
    elif cMax == r:
        h = 60.0 * (((g - b) / delta) % 6)
    elif cMax == g:
        h = 60.0 * (((b - r) / delta) + 2)
    else:
        h = 60.0 * (((r - g) / delta) + 4)
    
    # Compute s
    if cMax == 0:
        s = 0
    else:
        s = delta / cMax
    
    # Compute v
    v = cMax
    
    return (h, s, v)

def to_hsv(m):
    for i in range(0, 256):
        for j in range(0, 256):
            m[i,j] = rgb_to_hsv(m[i,j,0], m[i,j,1], m[i,j,2])
            
    return m

def histogram(m, iM, jM):
    sumH, sumS, sumV = 0, 0, 0
    for i in range (iM*4, iM*4+4):
        for j in range (jM*4, jM*4+4):
            sumH += m[i,j,0]
            sumS += m[i,j,1]
            sumV += m[i,j,2]
    
    return (sumH / 9, sumS / 9, sumV / 9)

def to_histogram(m):
    mHistogram = np.empty([64, 64, 3])
    for i in range(0, 64):
        for j in range(0, 64):
            mHistogram[i,j] = histogram(m, i, j)
            
    return mHistogram

def cosine_similarity(v1, v2):
    dot, norm_a, norm_b = 0, 0, 0
    for i in range(0, len(v1)):
        dot += v1[i] * v2[i]
        norm_a += math.pow(v1[i], 2)
        norm_b += math.pow(v2[i], 2)
        
    norm_a = math.sqrt(norm_a)
    norm_b = math.sqrt(norm_b)
    
    if norm_a * norm_b == 0:
        cos_theta = 0
    else:
        cos_theta = dot / (norm_a * norm_b)
        
    return cos_theta

def similarity(m1, m2):
    arr1 = np.reshape(m1, -1)
    arr2 = np.reshape(m2, -1)
    
    similarity = cosine_similarity(arr1, arr2)
    return similarity
