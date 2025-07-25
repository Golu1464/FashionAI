# Real color theory-based palette mapping
OUTFIT_PALETTES = {
    "Warm": {
        "Male": {
            "Casual": ["Olive", "Mustard", "Beige", "Terracotta", "Warm White"],
            "Formal": ["Camel", "Rust", "Dark Brown", "Khaki", "Ivory"],
            "Party": ["Coral", "Burnt Orange", "Gold", "Copper", "Maroon"],
            "Festive": ["Gold", "Saffron", "Maroon", "Cream", "Emerald"],
            "Daily": ["Beige", "Light Brown", "Off White", "Olive", "Khaki"]
        },
        "Female": {
            "Casual": ["Peach", "Coral", "Beige", "Olive", "Warm White"],
            "Formal": ["Bronze", "Terracotta", "Caramel", "Camel", "Ivory"],
            "Party": ["Burnt Orange", "Gold", "Copper", "Rose Gold", "Maroon"],
            "Festive": ["Rose Gold", "Rust Red", "Gold", "Emerald", "Ivory"],
            "Daily": ["Peach", "Beige", "Light Brown", "Olive", "Warm White"]
        },
        "Unisex": {
            "Casual": ["Warm White", "Beige", "Olive", "Rust", "Terracotta"],
            "Formal": ["Ivory", "Camel", "Dark Brown", "Gold", "Khaki"],
            "Party": ["Copper", "Maroon", "Burnt Orange", "Saffron", "Emerald"],
            "Festive": ["Gold", "Maroon", "Ivory", "Olive", "Emerald"],
            "Daily": ["Warm White", "Beige", "Light Brown", "Khaki", "Olive"]
        }
    },

    "Cool": {
        "Male": {
            "Casual": ["Navy", "Cool Grey", "Charcoal", "Sky Blue", "Plum"],
            "Formal": ["Black", "Steel Blue", "Slate Grey", "Deep Teal", "White"],
            "Party": ["Royal Blue", "Purple", "Emerald", "Cool Pink", "Silver"],
            "Festive": ["Royal Blue", "Emerald", "Steel Blue", "Silver", "Deep Purple"],
            "Daily": ["Cool Grey", "Sky Blue", "Charcoal", "White", "Slate"]
        },
        "Female": {
            "Casual": ["Lavender", "Sky Blue", "Cool Grey", "Plum", "Soft Pink"],
            "Formal": ["Navy", "Ice Blue", "Charcoal", "White", "Silver"],
            "Party": ["Fuchsia", "Cool Pink", "Royal Blue", "Emerald", "Purple"],
            "Festive": ["Fuchsia", "Silver", "Emerald", "Lavender", "Royal Blue"],
            "Daily": ["Lavender", "Cool Grey", "Sky Blue", "White", "Dusty Pink"]
        },
        "Unisex": {
            "Casual": ["Sky Blue", "Cool Grey", "Lavender", "Charcoal", "Dusty Blue"],
            "Formal": ["Steel Blue", "White", "Slate Grey", "Navy", "Black"],
            "Party": ["Royal Blue", "Purple", "Silver", "Emerald", "Cool Pink"],
            "Festive": ["Lavender", "Royal Blue", "Silver", "Emerald", "Charcoal"],
            "Daily": ["Cool Grey", "Sky Blue", "Charcoal", "White", "Dusty Blue"]
        }
    },

    "Neutral": {
        "Male": {
            "Casual": ["White", "Charcoal", "Beige", "Teal", "Dusty Blue"],
            "Formal": ["Navy", "Black", "Steel", "Olive", "Cream"],
            "Party": ["Champagne", "Wine", "Dusty Rose", "Midnight Blue", "Grey"],
            "Festive": ["Champagne", "Wine", "Deep Green", "Cream", "Slate Blue"],
            "Daily": ["Beige", "White", "Olive", "Dusty Blue", "Grey"]
        },
        "Female": {
            "Casual": ["Beige", "Blush", "Mauve", "Cream", "Dusty Blue"],
            "Formal": ["Taupe", "Black", "Olive", "Navy", "Cream"],
            "Party": ["Champagne", "Blush Pink", "Dusty Rose", "Wine", "Teal"],
            "Festive": ["Blush Pink", "Champagne", "Emerald", "Taupe", "Deep Purple"],
            "Daily": ["Mauve", "Beige", "Cream", "Blush", "Dusty Blue"]
        },
        "Unisex": {
            "Casual": ["Cream", "Beige", "Dusty Blue", "Olive", "Slate Grey"],
            "Formal": ["Taupe", "Steel", "Charcoal", "Cream", "Olive"],
            "Party": ["Champagne", "Wine", "Dusty Rose", "Teal", "Grey"],
            "Festive": ["Emerald", "Slate Blue", "Champagne", "Taupe", "Wine"],
            "Daily": ["Beige", "Cream", "Dusty Blue", "Mauve", "Grey"]
        }
    }
}


SKIN_TO_UNDERTONE_MAP = {
    "Fair": "Cool",
    "Medium": "Neutral",
    "Olive": "Neutral",
    "Tan": "Warm",
    "Dark": "Warm",
    "Very Dark": "Cool"
}

def get_outfit_suggestions(skin_tone, undertone, gender, outfit_type):
    """
    Return a list of color suggestions for top and bottom wear.
    Skin tone can help infer undertone if not explicitly provided.
    """
    # Use mapped undertone if 'Auto' or empty is selected
    if undertone in ["", "Auto", None]:
        undertone = SKIN_TO_UNDERTONE_MAP.get(skin_tone, "Neutral")

    gender = gender.capitalize()
    outfit_type = outfit_type.capitalize()
    undertone = undertone.capitalize()

    try:
        suggestions = OUTFIT_PALETTES[undertone][gender][outfit_type]
        top_colors = suggestions[:3]
        bottom_colors = suggestions[3:]
        return top_colors, bottom_colors
    except KeyError:
        return ["No suggestions available"], ["Please check inputs"]

