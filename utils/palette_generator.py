# from tkinter import font
from PIL import Image, ImageDraw, ImageFont
# from matplotlib.pyplot import draw, title

def generate_palette_image(top_colors, bottom_colors, skin_tone="", undertone=""):
    block_width = 100
    block_height = 100
    margin = 10
    label_height = 30
    section_spacing = 20
    title_height = 40

    # Total image width based on max color count
    max_colors = max(len(top_colors), len(bottom_colors))
    width = block_width * max_colors + margin * (max_colors + 1)
    height = (
        title_height +
        label_height +
        block_height +
        section_spacing +
        label_height +
        block_height +
        margin * 3
    )

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # Load a font
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # Draw title
    title = f"{skin_tone} - {undertone} Palette"
    bbox = draw.textbbox((0, 0), title, font=font)
    title_width = bbox[2] - bbox[0]

    draw.text(((width - title_width) / 2, margin), title, fill="black", font=font)

    # Draw Topwear Label
    y_top_label = title_height + margin
    draw.text((margin, y_top_label), "Topwear Palette", fill="black", font=font)

    # Draw Topwear Colors
    y_top_colors = y_top_label + label_height
    for i, color in enumerate(top_colors):
        x0 = margin + i * (block_width + margin)
        y0 = y_top_colors
        x1 = x0 + block_width
        y1 = y0 + block_height
        draw.rectangle([x0, y0, x1, y1], fill=color)

    # Draw Bottomwear Label
    y_bottom_label = y_top_colors + block_height + section_spacing
    draw.text((margin, y_bottom_label), "Bottomwear Palette", fill="black", font=font)

    # Draw Bottomwear Colors
    y_bottom_colors = y_bottom_label + label_height
    for i, color in enumerate(bottom_colors):
        x0 = margin + i * (block_width + margin)
        y0 = y_bottom_colors
        x1 = x0 + block_width
        y1 = y0 + block_height
        draw.rectangle([x0, y0, x1, y1], fill=color)

    return img
