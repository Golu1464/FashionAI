# app.py
import streamlit as st
# import cv2
import io
import numpy as np
# from PIL import Image
from utils.color_classification import extract_face_region, get_average_rgb, classify_skin_tone_lab, detect_undertone_hue
from utils.image_processing import load_image
from utils.outfit_suggestions import get_outfit_suggestions
from utils.palette_generator import generate_palette_image

COLOR_NAME_TO_HEX = {
    "Olive": "#808000", "Mustard": "#FFDB58", "Beige": "#F5F5DC", "Terracotta": "#E2725B",
    "Warm White": "#FDF4DC", "Camel": "#C19A6B", "Rust": "#B7410E", "Dark Brown": "#654321",
    "Khaki": "#F0E68C", "Ivory": "#FFFFF0", "Coral": "#FF7F50", "Burnt Orange": "#CC5500",
    "Gold": "#FFD700", "Copper": "#B87333", "Maroon": "#800000", "Peach": "#FFE5B4",
    "Bronze": "#CD7F32", "Caramel": "#FFDDA0", "Rose Gold": "#B76E79", "Navy": "#000080",
    "Cool Grey": "#8C92AC", "Charcoal": "#36454F", "Sky Blue": "#87CEEB", "Plum": "#8E4585",
    "Black": "#000000", "Steel Blue": "#4682B4", "Slate Grey": "#708090", "Deep Teal": "#003333",
    "White": "#FFFFFF", "Royal Blue": "#4169E1", "Purple": "#800080", "Emerald": "#50C878",
    "Cool Pink": "#F49AC2", "Silver": "#C0C0C0", "Lavender": "#E6E6FA", "Soft Pink": "#FFB6C1",
    "Ice Blue": "#AFDBF5", "Fuchsia": "#FF00FF", "Blush": "#F9C0C4", "Mauve": "#E0B0FF",
    "Cream": "#FFFDD0", "Taupe": "#483C32", "Champagne": "#F7E7CE", "Wine": "#722F37",
    "Dusty Rose": "#C08081", "Midnight Blue": "#191970", "Grey": "#808080", "Blush Pink": "#FE828C",
    "Teal": "#008080", "Dusty Blue": "#A6C8E2", "Steel": "#71797E", "Ivory White": "#FFFFF0",
    "Deep Green": "#004d00", "Slate Blue": "#6A5ACD", "Emerald Green": "#50C878", "Deep Purple": "#673AB7",
    "Dark Beige": "#D6AE7B", "Light Brown": "#A52A2A", "Off White": "#FAF9F6","Golden Yellow": "#FFDF00",
    "Deep Red": "#850101", "Bright Yellow": "#FFFF00", "Light Grey": "#D3D3D3",
    "Dark Grey": "#A9A9A9", "Light Blue": "#ADD8E6", "Dark Blue": "#00008B",
    "Bright Red": "#FF0000", "Bright Green": "#00FF00","Sapphire": "#0F52BA",
    "Sea Green": "#2E8B57",
    "Bright White": "#F5F5F5",
    "Pearl White": "#F8F6F0",

}


st.set_page_config(page_title="ToneMatchAI - Skin Tone Outfit Suggester", layout="centered")
st.title("🎨 ToneMatchAI")
st.write("Welcome to ToneMatchAI – Get fashion color suggestions based on your skin tone and undertone.")

mode = st.sidebar.radio("Choose Mode", ["📸 Auto Detect (Image)", "🧑 Manual Selection"])

if mode == "📸 Auto Detect (Image)":
    st.header("📸 Upload or Capture Image")
    st.markdown("> 📌 **Tip**: Upload a clear image of your face and visible skin (neck/arms), avoid filters or shadows.")
    input_method = st.radio("Select Input", ["Upload Image", "Use Webcam"])
    image = None

    if input_method == "Upload Image":
        uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded:
            image = load_image(uploaded)

    elif input_method == "Use Webcam":
        camera_image = st.camera_input("Take a photo")
        if camera_image:
            image = load_image(camera_image)

    if image:
        st.image(image, caption="Input Image", use_column_width=True)

        with st.spinner("Analyzing skin tone..."):
            img_np = np.array(image.convert("RGB"))
            region = extract_face_region(img_np)
            if region is None:
                st.error("Face not detected. Please upload a clearer image.")
            else:
                skin_rgb = get_average_rgb(region)
                tone_category = classify_skin_tone_lab(skin_rgb)
                undertone = detect_undertone_hue(skin_rgb)
                skin_hex = '#%02x%02x%02x' % skin_rgb

                st.subheader("🎯 Detected Skin Details")
                st.write(f"Skin Tone: **{tone_category}**")
                st.write(f"Undertone: **{undertone}**")
                st.markdown(
                    f"Detected Color: <div style='width:100px;height:30px;background-color:{skin_hex};border-radius:5px;'></div>",
                    unsafe_allow_html=True
                )

                st.markdown("---")
                st.subheader("👚 Outfit Suggestions")

                gender = st.selectbox("Select Gender", ["Female", "Male", "Unisex"])
                outfit_type = st.selectbox("Outfit Type", ["Party", "Casual", "Formal", "Festive", "Daily"])
                top_colors, bottom_colors = get_outfit_suggestions(tone_category, undertone, gender, outfit_type)

                st.markdown("**Topwear Suggestions**")
                cols1 = st.columns(len(top_colors))
                for i, color_name in enumerate(top_colors):
                    hex_val = COLOR_NAME_TO_HEX.get(color_name, "#CCCCCC")
                    with cols1[i]:
                        st.markdown(f"<div style='width:60px;height:60px;background-color:{hex_val};border-radius:8px;'></div>", unsafe_allow_html=True)

                st.markdown("**Bottomwear Suggestions**")
                cols2 = st.columns(len(bottom_colors))
                for i, color_name in enumerate(bottom_colors):
                    hex_val = COLOR_NAME_TO_HEX.get(color_name, "#CCCCCC")
                    with cols2[i]:
                        st.markdown(f"<div style='width:60px;height:60px;background-color:{hex_val};border-radius:8px;'></div>", unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📅 Download Color Palette Image"):
                    top_hex_colors = [COLOR_NAME_TO_HEX.get(c, "#CCCCCC") for c in top_colors]
                    bottom_hex_colors = [COLOR_NAME_TO_HEX.get(c, "#CCCCCC") for c in bottom_colors]

                    palette_img = generate_palette_image(top_hex_colors, bottom_hex_colors, tone_category, undertone)
                    st.image(palette_img, caption="Downloadable Outfit Palette")

                    buf = io.BytesIO()
                    palette_img.save(buf, format="PNG")
                    byte_im = buf.getvalue()

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.download_button("Download as PNG", data=byte_im, file_name="color_palette.png", mime="image/png")


elif mode == "🧑 Manual Selection":
    st.header("🧑 Manual Outfit Suggestion")
    skin_tone = st.selectbox("Select Skin Tone", ["Fair", "Medium", "Olive", "Tan", "Dark", "Very Dark"])
    undertone = st.selectbox("Select Undertone", ["Warm", "Cool", "Neutral"])
    gender = st.selectbox("Gender", ["Female", "Male", "Unisex"])
    outfit_type = st.selectbox("Outfit Type", ["Party", "Casual", "Formal", "Festive", "Daily"])

    st.markdown("---")
    st.subheader("👕 Suggested Outfit Colors")

    top_colors, bottom_colors = get_outfit_suggestions(skin_tone, undertone, gender, outfit_type)

    st.markdown("**Topwear Suggestions**")
    cols1 = st.columns(len(top_colors))
    for i, color_name in enumerate(top_colors):
        hex_val = COLOR_NAME_TO_HEX.get(color_name, "#CCCCCC")
        with cols1[i]:
            st.markdown(f"<div style='width:60px;height:60px;background-color:{hex_val};border-radius:8px;'></div>", unsafe_allow_html=True)

    st.markdown("**Bottomwear Suggestions**")
    cols2 = st.columns(len(bottom_colors))
    for i, color_name in enumerate(bottom_colors):
        hex_val = COLOR_NAME_TO_HEX.get(color_name, "#CCCCCC")
        with cols2[i]:
            st.markdown(f"<div style='width:60px;height:60px;background-color:{hex_val};border-radius:8px;'></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📅 Download Color Palette Image"):
        top_hex_colors = [COLOR_NAME_TO_HEX.get(c, "#CCCCCC") for c in top_colors]
        bottom_hex_colors = [COLOR_NAME_TO_HEX.get(c, "#CCCCCC") for c in bottom_colors]

        palette_img = generate_palette_image(top_hex_colors, bottom_hex_colors, skin_tone, undertone)
        st.image(palette_img, caption="Downloadable Outfit Palette")

        buf = io.BytesIO()
        palette_img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("Download as PNG", data=byte_im, file_name="color_palette.png", mime="image/png")

st.markdown("---")
st.caption("Built with ❤️ by Sonu Kumar Sharma – ToneMatchAI")
