import cv2
import numpy as np
from skimage import color

def extract_face_region(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0:
        return None
    x, y, w, h = faces[0]
    cx, cy, cw, ch = x + w//4, y + h//3, w//2, h//3
    return image[cy:cy+ch, cx:cx+cw]

def get_average_rgb(region):
    avg_color = region.mean(axis=0).mean(axis=0)
    return tuple(int(c) for c in avg_color)

def classify_skin_tone_lab(rgb):
    rgb_arr = np.array([[rgb]], dtype=np.uint8)
    lab = color.rgb2lab(rgb_arr / 255.0)
    L = lab[0][0][0]
    if L > 80:
        return "Fair"
    elif L > 70:
        return "Medium"
    elif L > 60:
        return "Olive"
    elif L > 50:
        return "Tan"
    elif L > 40:
        return "Dark"
    else:
        return "Very Dark"

def detect_undertone_hue(rgb):
    rgb_arr = np.uint8([[list(rgb)]])
    hsv = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2HSV)[0][0]
    hue = hsv[0]
    if 0 <= hue <= 25 or hue >= 330:
        return "Warm"
    elif 90 <= hue <= 150:
        return "Cool"
    else:
        return "Neutral"
