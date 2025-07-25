from PIL import Image
import numpy as np
import cv2
from sklearn.cluster import KMeans

def load_image(uploaded_file):
    """
    Load uploaded image into PIL format.
    Accepts a file-like object (like from Streamlit uploader).
    """
    image = Image.open(uploaded_file).convert("RGB")
    return image


def extract_skin_color(pil_img, n_colors=3):
    """
    Extract dominant skin tones from detected face or skin region using better filtering.
    Returns a list of (RGB tuple, HEX string).
    """
    img = np.array(pil_img.convert("RGB"))
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    mask = np.zeros(gray.shape, dtype=np.uint8)

    if len(faces) > 0:
        x, y, w, h = faces[0]
        # Slightly shrink the face box to avoid eyes/lips/hair
        padding_x = int(w * 0.1)
        padding_y = int(h * 0.1)
        mask[y+padding_y:y+h-padding_y, x+padding_x:x+w-padding_x] = 255
    else:
        mask[:] = 255  # use full image if face not detected

    # Define HSV skin color range
    lower_skin = np.array([0, 20, 60], dtype=np.uint8)
    upper_skin = np.array([25, 200, 255], dtype=np.uint8)
    skin_mask = cv2.inRange(img_hsv, lower_skin, upper_skin)
    combined_mask = cv2.bitwise_and(skin_mask, skin_mask, mask=mask)

    # Extract skin pixels
    skin_pixels = img[combined_mask > 0]

    if len(skin_pixels) < 50:
        # Not enough skin pixels, return fallback
        fallback_rgb = (200, 160, 140)
        fallback_hex = '#%02x%02x%02x' % fallback_rgb
        return [(fallback_rgb, fallback_hex)]

    # Use KMeans clustering to find dominant skin colors
    n_clusters = min(n_colors, len(skin_pixels))
    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    kmeans.fit(skin_pixels)
    centers = np.round(kmeans.cluster_centers_).astype(int)

    top_colors = []
    for center in centers:
        rgb = tuple(np.clip(center, 0, 255))
        hex_val = '#%02x%02x%02x' % rgb
        top_colors.append((rgb, hex_val))

    return top_colors
