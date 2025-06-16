import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import font_manager
import streamlit as st
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# --- Load custom font ---
font_path = "NotoSans-VariableFont_wdth,wght.ttf"
font_prop = font_manager.FontProperties(fname=font_path)
mpl.rcParams['font.family'] = font_prop.get_name()

# --- Streamlit Config ---
st.set_page_config(page_title="Distance Covered Dashboard", layout="wide")

# --- Custom CSS ---
st.markdown(f"""
    <style>
        @font-face {{
            font-family: 'Roboto Condensed';
            src: url('RobotoCondensed-VariableFont_wght.ttf');
        }}
        html, body, .stApp {{
            background-color: #171717 !important;
            color: white !important;
            font-family: 'Roboto Condensed', sans-serif !important;
        }}
        header, footer, section {{
            background-color: #171717 !important;
        }}
        [data-testid="stSidebar"] {{
            background-color: #1e1e1e !important;
        }}
        h1, h2, h3, h4, h5, h6, p, span, div {{
            color: white !important;
        }}
        button {{
            background-color: #3F1F5A !important;
            color: white !important;
        }}
    </style>
""", unsafe_allow_html=True)

# --- Logo ---
st.image("logo.jpg", use_container_width=True)

# --- Intro ---
st.markdown("""
Welcome to the Distance Covered Dashboard!  
This platform celebrates the amazing efforts of all the teams taking part.

[👉 Donate to support LionHeart](https://www.justgiving.com/team/sdl-lhh25)
""", unsafe_allow_html=True)

# --- Load Data ---
df = pd.read_csv("data.csv")

# --- Image loading ---
#male_imgs = [mpimg.imread(f"male_runner_0{i}.png") for i in range(1, 5)]
#female_imgs = [mpimg.imread(f"female_runner_0{i}.png") for i in range(1, 5)]
flag_img = mpimg.imread("checkered_flag.png")
start_img = mpimg.imread("start_icon.png")  # optional icon for "start" (replace if you have a better one)

#def get_runner_icon(img, zoom=0.05):
#    return OffsetImage(img, zoom=zoom, resample=True)
# --- Map League to League Number ---
league_to_number = df.drop_duplicates(subset=['League'])[['League', 'League Number']].set_index('League')['League Number'].to_dict()

# --- Load Images by League ---

# --- Load images from league-specific folder ---
def load_league_images(league_number):
    folder_path = os.path.join("images", str(league_number))
    if not os.path.exists(folder_path):
        return []
    image_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".png")])
    image_paths = [os.path.join(folder_path, f) for f in image_files]
    images = [mpimg.imread(img_path) for img_path in image_paths]
    return images

# --- Updated Plotting Function ---
# --- Plotting Function ---
def plot_league_data(league_df, league_name):
    df_sorted = league_df.sort_values(by="% Distance Covered").reset_index(drop=True)
    league_number = league_to_number.get(league_name, 1)
    runner_images = load_league_images(league_number)
    if not runner_images:
        return plt.figure()

    fig, ax = plt.subplots(figsize=(14, 0.65 * len(df_sorted)))
    fig.patch.set_facecolor('#171717')
    ax.set_facecolor('#171717')
    ax.axis('off')

    bar_height = 0.7
    y_positions = range(len(df_sorted))
    ax.barh(y=y_positions, width=df_sorted['% Distance Covered'], height=bar_height, color=(0, 0, 0, 0))

    # Alternate runner icons
    for i, value in enumerate(df_sorted['% Distance Covered']):
        img = runner_images[i % len(runner_images)]
        icon = OffsetImage(img, zoom=0.05, resample=True)
        ab = AnnotationBbox(icon, (value, i), frameon=False, box_alignment=(0.5, 0.5))
        ax.add_artist(ab)

    # Labels
    for i, (value, name) in enumerate(zip(df_sorted['% Distance Covered'], df_sorted['Team Name'])):
        ax.text(x=value - 2.5, y=i, s=name, ha='right', va='center',
                fontsize=18, color='white', weight='bold', fontproperties=font_prop)
        label_text = "" if value == 0 else f"{value:.1f}%"
        ax.text(x=value + 2.5, y=i, s=label_text, ha='left', va='center',
                fontsize=16, color='white', fontproperties=font_prop)

    ax.set_xlim(0, 110)
    ax.set_ylim(-1, y_positions[-1] + 1.2)
    # Start line & whistle
    start_y = len(df_sorted) - 0.5 + 0.2
    top_y = y_positions[-1] + 0.75  # First (top) bar's y-position
    ax.axvline(x=0, color='#555555', linestyle='--', linewidth=0.5)
    start_flag_img = mpimg.imread("whistle.png")
    start_icon = OffsetImage(start_flag_img, zoom=0.05)
    ab_start = AnnotationBbox(start_icon, (0, start_y), frameon=False, box_alignment=(0.5, 0))
    ax.add_artist(ab_start)

    # Finish line & flag
    ax.axvline(x=100, color='#AAAAAA', linestyle='--', linewidth=0.5)
    flag_img = mpimg.imread("checkered_flag.png")
    flag_icon = OffsetImage(flag_img, zoom=0.05)
    ab_flag = AnnotationBbox(flag_icon, (102.5, start_y), frameon=False, box_alignment=(0.5, 0))
    ax.add_artist(ab_flag)

    return fig


# --- Display Each League ---
for league in df['League'].unique():
    st.markdown(f"### {league}")
    league_df = df[df['League'] == league]
    fig = plot_league_data(league_df, league)
    st.pyplot(fig)
