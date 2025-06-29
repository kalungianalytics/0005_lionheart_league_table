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
st.set_page_config(page_title="Lionheart 2025 HQ Hop League Tables", layout="wide")

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

# --- Credits ---
st.markdown("""
    <div style='
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 1.5rem;
        margin-bottom: 2.5rem;
        font-size: 16px;
        color: #CCCCCC;
    '>
        <span>Designed by <strong>Kalungi Analytics</strong> · 
            <a href='https://www.linkedin.com/in/ben-sharpe-49659a207/' target='_blank' style='color: #FF6B6B; text-decoration: none; margin-left: 4px;'>
                Connect on LinkedIn
            </a>
        </span>
    </div>
""", unsafe_allow_html=True)


# --- Logo ---
st.image("logo.jpg", use_container_width=True)



# --- Intro ---
#st.markdown("""
#Please consider donating to support the amazing efforts of our teams!  

#[👉 Donate to support LionHeart](https://www.justgiving.com/team/sdl-lhh25)
#""", unsafe_allow_html=True)

# --- Donate Banner ---
st.markdown("""
    <div style='
        background-color:#3F1F5A;
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
        margin-bottom: 2rem;
    '>
        <h2 style='color: white; margin-bottom: 1rem;'>Please consider donating to Lionheart to support the amazing efforts of our teams!</h2>
        <a href='https://www.justgiving.com/team/sdl-lhh25' target='_blank' style='
            background-color: #FF6B6B;
            color: white;
            padding: 0.75rem 1.5rem;
            text-decoration: none;
            border-radius: 0.5rem;
            font-weight: bold;
            font-size: 1.1rem;
            display: inline-block;
            max-width: 100%;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        '>💖 Donate Now</a>
    </div>
    
    <h1 style='text-align:center; margin-top:-1rem;'>League Tables – Week Two</h3>
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
    ax.axvline(x=0, color='#eeeeee', linestyle='--', linewidth=0.75)
    start_flag_img = mpimg.imread("whistle.png")
    start_icon = OffsetImage(start_flag_img, zoom=0.05)
    ab_start = AnnotationBbox(start_icon, (0, start_y), frameon=False, box_alignment=(0.5, 0))
    ax.add_artist(ab_start)

    # Finish line & flag
    ax.axvline(x=100, color='#eeeeee', linestyle='--', linewidth=0.75)
    flag_img = mpimg.imread("checkered_flag.png")
    flag_icon = OffsetImage(flag_img, zoom=0.05)
    ab_flag = AnnotationBbox(flag_icon, (102.5, start_y), frameon=False, box_alignment=(0.5, 0))
    ax.add_artist(ab_flag)

    return fig


# --- Display Each League ---
for league in df['League'].unique():
    st.markdown(f"## {league}")
    league_df = df[df['League'] == league]
    fig = plot_league_data(league_df, league)
    st.pyplot(fig)

# --- Donate Banner ---
st.markdown("""
 <div style='
        background-color:#3F1F5A;
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
        margin-bottom: 2rem;
    '>
        <h2 style='color: white; margin-bottom: 1rem;'>Please consider donating to Lionheart to support the amazing efforts of our teams!</h2>
        <a href='https://www.justgiving.com/team/sdl-lhh25' target='_blank' style='
            background-color: #FF6B6B;
            color: white;
            padding: 0.75rem 1.5rem;
            text-decoration: none;
            border-radius: 0.5rem;
            font-weight: bold;
            font-size: 1.1rem;
            display: inline-block;
            max-width: 100%;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        '>💖 Donate Now</a>
    </div>
""", unsafe_allow_html=True)