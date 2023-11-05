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
    for i in range(0, 85):
        for j in range(0, 85):
            m[i,j] = rgb_to_hsv(m[i,j,0], m[i,j,1], m[i,j,2])
            
    return m

def histogram(m, iM, jM):
    sumR, sumG, sumB = 0, 0, 0
    for i in range (iM*3, iM*3+3):
        for j in range (jM*3, jM*3+3):
            sumR += m[i,j,0]
            sumG += m[i,j,1]
            sumB += m[i,j,2]
    
    return (sumR, sumG, sumB)

def to_histogram(m):
    mHistogram = np.empty([85, 85, 3])
    for i in range(0, 85):
        for j in range(0, 85):
            sumRGB = histogram(m, i, j)
            mHistogram[i,j] = sumRGB
            
    return mHistogram

def cosine_similarity(v1, v2):
    dot, norm_a, norm_b = 0, 0, 0
    for i in range(0, len(v1)):
        dot += v1[i] * v2[i]
        norm_a += math.pow(v1[i], 2)
        norm_b += math.pow(v2[i], 2)
        
    norm_a = math.sqrt(norm_a)
    norm_b = math.sqrt(norm_b)
    
    cos_theta = dot / (norm_a * norm_b)
    return cos_theta

def similarity(m1, m2):
    m_similarity = np.empty([85, 85])
    for i in range(0, 85):
        for j in range(0, 85):
            m_similarity[i,j] = cosine_similarity(m1[i,j], m2[i,j])
    
    similarity = np.sum(m_similarity) / (85*85)
    return similarity