import streamlit as st
import numpy as np
import pandas as pd
import cv2
from PIL import Image
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
from matplotlib.colors import to_rgb
import io
import base64
from category_palettes import category_palettes  # Assuming this is a separate module with predefined palettes

# Load model
import joblib
# pipeline = joblib.load("color_recommender.pkl")

# Hardcoded palette dictionary as placeholder for specific category results
# category_palettes = {
#     ("Fair", "Cool", "Female", "Party"): [[255, 182, 193], [173, 216, 230], [221, 160, 221], [240, 248, 255], [255, 240, 245]],
#     ("Medium", "Neutral", "Female", "Party"): [[255, 140, 0], [255, 105, 180], [72, 209, 204], [255, 160, 122], [199, 21, 133]],
#     ("Dark", "Warm", "Male", "Formal"): [[139, 69, 19], [184, 134, 11], [160, 82, 45], [205, 133, 63], [218, 165, 32]],
#     ("Olive", "Cool", "Unisex", "Daily"): [[70, 130, 180], [100, 149, 237], [0, 191, 255], [176, 224, 230], [95, 158, 160]]
#     # Add more specific combinations as needed
# }

class PaletteModel:
    def predict(self, X):
        row = X.iloc[0]
        key = (row['SkinToneCategory'], row['UndertoneType'], row['Gender'], row['Suggested_For'])
        return np.array(category_palettes.get(key, [[102, 205, 170], [255, 105, 180], [75, 0, 130], [255, 165, 0], [70, 130, 180]])).flatten()

pipeline = PaletteModel()

# Helper Functions
def load_image(image_file):
    img = Image.open(image_file)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def detect_face(img_bgr):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0:
        return None
    x, y, w, h = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
    return img_bgr[y:y+h, x:x+w]

def extract_skin(face_img):
    hsv = cv2.cvtColor(face_img, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 20, 70], dtype=np.uint8)
    upper = np.array([20, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower, upper)
    return face_img[mask > 0]

def get_dominant_color(pixels):
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10).fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)
    counts = np.bincount(kmeans.labels_)
    return colors[np.argmax(counts)]

def classify_skin(rgb):
    b, g, r = rgb
    brightness = (r + g + b) / 3
    if brightness >= 210: return "Fair"
    elif brightness >= 170: return "Medium"
    elif brightness >= 130: return "Olive"
    elif brightness >= 100: return "Tan"
    elif brightness >= 70: return "Dark"
    else: return "Very Dark"

def estimate_undertone(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    if r > g and b > g:
        return "Cool"
    elif g > b and r > b:
        return "Warm"
    return "Neutral"

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % tuple(np.clip(np.array(rgb, dtype=int), 0, 255))

def suggest_colors(skin_tone, undertone, gender, outfit, model):
    df = pd.DataFrame([{
        "SkinToneCategory": skin_tone,
        "UndertoneType": undertone,
        "Gender": gender,
        "Suggested_For": outfit
    }])
    preds = model.predict(df).reshape(5, 3)
    if preds.max() <= 1.0:
        preds *= 255
    return [rgb_to_hex(p) for p in preds]

def plot_palette(hex_colors):
    fig, ax = plt.subplots(1, 5, figsize=(10, 2))
    for i, hex_color in enumerate(hex_colors):
        ax[i].imshow([[to_rgb(hex_color)]])
        ax[i].set_title(hex_color, fontsize=8)
        ax[i].axis('off')
    plt.tight_layout()
    return fig

def download_palette(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return buf

# Streamlit App
st.set_page_config(layout="wide")
st.title("🎨 Skin Tone Based Outfit Color Palette Generator")

option = st.sidebar.selectbox("Choose Mode", [
    "1️⃣ Upload Image to Generate Report", 
    "2️⃣ Manual Input Color Suggestion", 
    "3️⃣ Educational Universal Report"
])

if option.startswith("1"):
    st.header("📷 Upload Image to Generate Color Palette")
    image_file = st.file_uploader("Upload Image or Capture", type=['jpg', 'png', 'jpeg'])
    if image_file is not None:
        img_bgr = load_image(image_file)
        face = detect_face(img_bgr)
        if face is None:
            st.error("No face detected!")
        else:
            skin_pixels = extract_skin(face)
            dominant_rgb = get_dominant_color(skin_pixels)
            skin_tone = classify_skin(dominant_rgb)
            undertone = estimate_undertone(dominant_rgb)
            st.success(f"Detected Skin Tone: {skin_tone}")
            st.success(f"Undertone: {undertone}")
            gender = st.selectbox("Select Gender", ["Male", "Female", "Unisex"])
            outfit = st.selectbox("Occasion", ["Casual", "Formal", "Party", "Festive", "Daily"])
            hex_colors = suggest_colors(skin_tone, undertone, gender, outfit, pipeline)
            fig = plot_palette(hex_colors)
            st.pyplot(fig)
            buf = download_palette(fig)
            st.download_button("📥 Download Palette", data=buf, file_name="palette.png")

elif option.startswith("2"):
    st.header("✍️ Manual Input for Palette Recommendation")
    skin_tone = st.selectbox("Select Skin Tone", ["Very Dark", "Dark", "Tan", "Olive", "Medium", "Fair"])
    undertone = st.selectbox("Select Undertone", ["Cool", "Warm", "Neutral"])
    gender = st.selectbox("Select Gender", ["Male", "Female", "Unisex"])
    outfit = st.selectbox("Occasion", ["Casual", "Party", "Formal", "Festive", "Daily"])
    if st.button("Generate Palette"):
        hex_colors = suggest_colors(skin_tone, undertone, gender, outfit, pipeline)
        fig = plot_palette(hex_colors)
        st.pyplot(fig)
        buf = download_palette(fig)
        st.download_button("📥 Download Palette", data=buf, file_name="manual_palette.png")

elif option.startswith("3"):
    st.header("📚 Educational Fashion Report")
    st.markdown("This report provides universal guidance on color combinations, outfit matching, and fashion suggestions for various skin tones and undertones.")

# ✅ Valid skin tone reference image
    # ✅ Load your local image for MEN
    st.markdown("**<span style='font-size:18px;'>Men's Skin Tone Palette</span>**", unsafe_allow_html=True)
    st.image("08d55e0b8465e292e4feb848b6b695f6.jpg", use_column_width=True)

# ✅ Load your local image for WOMEN
    st.markdown("**<span style='font-size:18px;'>Women's Skin Tone Palette</span>**", unsafe_allow_html=True)
    st.image("march-Blog-skin-tone-color-chart.jpg", use_column_width=True)

    # --- Skin Tone Categories ---
    st.markdown("### 🎨 Skin Tone Categories & Suggested Colors:")

    st.markdown("#### 🧴 Fair to Medium")
    st.write("Pastels, cool blues, soft greys")
    st.color_picker("Pastel Pink", "#FFD1DC", key="fair_pink", label_visibility="collapsed")
    st.color_picker("Sky Blue", "#87CEEB", key="fair_sky", label_visibility="collapsed")
    st.color_picker("Light Grey", "#D3D3D3", key="fair_grey", label_visibility="collapsed")

    st.markdown("#### 🌿 Olive to Tan")
    st.write("Earthy tones, bold oranges, deep reds")
    st.color_picker("Olive Green", "#808000", key="olive_olive", label_visibility="collapsed")
    st.color_picker("Burnt Orange", "#CC5500", key="olive_orange", label_visibility="collapsed")
    st.color_picker("Crimson", "#DC143C", key="olive_crimson", label_visibility="collapsed")

    st.markdown("#### 🌑 Dark to Very Dark")
    st.write("Jewel tones, metallics, rich neutrals")
    st.color_picker("Emerald", "#50C878", key="dark_emerald", label_visibility="collapsed")
    st.color_picker("Gold", "#FFD700", key="dark_gold", label_visibility="collapsed")
    st.color_picker("Plum", "#8E4585", key="dark_plum", label_visibility="collapsed")

    # --- Undertone Matching ---
    st.markdown("### 🌈 Undertone Matching:")

    st.markdown("#### ❄️ Cool Undertones")
    st.write("Silver, navy, emerald")
    st.color_picker("Silver", "#C0C0C0", key="cool_silver", label_visibility="collapsed")
    st.color_picker("Navy", "#000080", key="cool_navy", label_visibility="collapsed")
    st.color_picker("Emerald", "#50C878", key="cool_emerald", label_visibility="collapsed")

    st.markdown("#### 🔥 Warm Undertones")
    st.write("Gold, peach, olive green")
    st.color_picker("Gold", "#FFD700", key="warm_gold", label_visibility="collapsed")
    st.color_picker("Peach", "#FFE5B4", key="warm_peach", label_visibility="collapsed")
    st.color_picker("Olive Green", "#808000", key="warm_olive", label_visibility="collapsed")

    st.markdown("#### 🧊 Neutral Undertones")
    st.write("Most colors; balance is key")
    st.color_picker("Taupe", "#483C32", key="neutral_taupe", label_visibility="collapsed")
    st.color_picker("Rose Brown", "#A1625B", key="neutral_rose", label_visibility="collapsed")
    st.color_picker("Slate", "#708090", key="neutral_slate", label_visibility="collapsed")

    # --- Gender-based Suggestions ---
    st.markdown("### 🚻 Gender-based Styling Tips:")

    st.markdown("#### 👔 Male")
    st.write("- Structured outfits\n- Layering with contrast\n- Blues, greys, deep greens")

    st.markdown("#### 👗 Female")
    st.write("- Flowing silhouettes\n- Complementary palettes\n- Pastels, blush, warm tones")

    st.markdown("#### 🧥 Unisex")
    st.write("- Minimalist bases with bold accents\n- Monochrome layering")

    # End section
    st.markdown("👉 Try Modes 1 or 2 in the app for personalized AI-based outfit suggestions!")

st.markdown("---")
st.caption("Built with ❤️ by Sonu Kumar Sharma – FashionAI")