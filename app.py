# --- Imports ---
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import font_manager
import streamlit as st
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg

# ============================== #
#         STYLING SETUP         #
# ============================== #

# --- Load and set global font for Matplotlib ---
font_path = "NotoSans-VariableFont_wdth,wght.ttf"
font_prop = font_manager.FontProperties(fname=font_path)
mpl.rcParams['font.family'] = font_prop.get_name()

# --- Streamlit page configuration ---
st.set_page_config(page_title="Lionheart 2025 HQ Hop League Tables", layout="wide")

# --- Apply dark theme and custom font styling ---
st.markdown("""
    <style>
        @font-face {
            font-family: 'Roboto Condensed';
            src: url('RobotoCondensed-VariableFont_wght.ttf');
        }
        html, body, .stApp {
            background-color: #171717 !important;
            color: white !important;
            font-family: 'Roboto Condensed', sans-serif !important;
        }
        [data-testid="stSidebar"] {
            background-color: #1e1e1e !important;
        }
        h1, h2, h3, h4, h5, h6, p, span, div {
            color: white !important;
        }
        button {
            background-color: #3F1F5A !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Increase font size for radio button labels ---
st.markdown("""
    <style>
        label[data-testid="stMarkdownContainer"] + div div[role="radiogroup"] label {
            font-size: 1.125rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# ============================== #
#        HEADER + BANNER        #
# ============================== #

# --- Credits banner ---
st.markdown("""
    <div style='display: flex; justify-content: center; align-items: center; margin-top: 1.5rem; margin-bottom: 2.5rem; font-size: 16px; color: #CCCCCC;'>
        <span>Designed by <strong>Kalungi Analytics</strong> · 
            <a href='https://www.linkedin.com/in/ben-sharpe-49659a207/' target='_blank' style='color: #FF6B6B; text-decoration: none; margin-left: 4px;'>
                Connect on LinkedIn
            </a>
        </span>
    </div>
""", unsafe_allow_html=True)

# --- Display logo (use file path directly) ---
logo_path = "images/logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, use_container_width=True)
else:
    st.warning("Logo not found.")

# --- Initial donate banner ---
st.markdown("""
    <div style='background-color:#3F1F5A; padding: 1.5rem; border-radius: 1rem; text-align: center; margin-bottom: 2rem;'>
        <h2 style='color: white; margin-bottom: 1rem;'>Please consider donating to Lionheart to support the amazing efforts of our teams!</h2>
        <a href='https://www.justgiving.com/team/sdl-lhh25' target='_blank' style='background-color: #FF6B6B; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 0.5rem; font-weight: bold; font-size: 1.1rem; display: inline-block;'>💖 Donate Now</a>
    </div>
""", unsafe_allow_html=True)

# ============================== #
#        DATA LOADING SETUP     #
# ============================== #

# --- Load data with caching ---
@st.cache_data(show_spinner=False)
def load_data():
    return pd.read_csv("data.csv")

# --- Safe image loader with warning ---
def safe_load_image(path):
    if os.path.exists(path):
        return mpimg.imread(path)
    else:
        st.warning(f"Missing image: {path}")
        return None

# --- Load league-specific runner icons ---
def load_league_images(league_number):
    folder_path = os.path.join("images", str(league_number))
    if not os.path.exists(folder_path):
        return []
    image_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".png")])
    return [safe_load_image(os.path.join(folder_path, f)) for f in image_files if safe_load_image(os.path.join(folder_path, f)) is not None]

# --- Load all data and images ---
df = load_data()
flag_img = safe_load_image("images/checkered_flag.png")
start_img = safe_load_image("images/start_icon.png")
whistle_img = safe_load_image("images/whistle.png")

# --- Map League name to numeric ID ---
league_to_number = df.drop_duplicates(subset=['League'])[['League', 'League Number']].set_index('League')['League Number'].to_dict()

# ============================== #
#       PLOTTING FUNCTION        #
# ============================== #

def plot_league_data(league_df, league_name, flag_img, start_img, whistle_img):
    df_sorted = league_df.sort_values(by="% Distance Covered").reset_index(drop=True)
    league_number = league_to_number.get(league_name, 1)
    runner_images = load_league_images(league_number)

    if not runner_images or df_sorted.empty:
        return plt.figure()

    max_bars = 20
    num_bars = min(len(df_sorted), max_bars)

    fig, ax = plt.subplots(figsize=(14, 0.65 * num_bars))
    fig.patch.set_facecolor('#171717')
    ax.set_facecolor('#171717')
    ax.axis('off')

    bar_height = 0.7
    y_positions = range(num_bars)
    ax.barh(y=y_positions, width=df_sorted['% Distance Covered'][:num_bars], height=bar_height, color=(0, 0, 0, 0))

    # --- Runner icons ---
    for i, value in enumerate(df_sorted['% Distance Covered'][:num_bars]):
        img = runner_images[i % len(runner_images)]
        if img is not None:
            icon = OffsetImage(img, zoom=0.05, resample=True)
            ab = AnnotationBbox(icon, (value, i), frameon=False, box_alignment=(0.5, 0.5))
            ax.add_artist(ab)

    # --- Labels and values ---
    for i, (value, name) in enumerate(zip(df_sorted['% Distance Covered'][:num_bars], df_sorted['Team Name'][:num_bars])):
        ax.text(x=value - 2.5, y=i, s=name, ha='right', va='center',
                fontsize=16, color='white', weight='bold', fontproperties=font_prop)
        label_text = "" if value == 0 else f"{value:.1f}%"
        label_color = '#80CFA9' if value >= 100 else '#FFD700' if value >= 85 else '#FF6B6B'
        ax.text(x=value + 4.5, y=i, s=label_text, ha='left', va='center',
                fontsize=14, color=label_color, fontproperties=font_prop)

    max_value = df_sorted['% Distance Covered'][:num_bars].max()
    ax.set_xlim(0, max(110, max_value + 5))
    ax.set_ylim(-1, y_positions[-1] + 1.2)

    start_y = num_bars - 0.5 + 0.2
    ax.axvline(x=0, color='#eeeeee', linestyle='--', linewidth=0.75)
    if whistle_img is not None:
        ax.add_artist(AnnotationBbox(OffsetImage(whistle_img, zoom=0.05), (0, start_y), frameon=False, box_alignment=(0.5, 0)))
    ax.axvline(x=100, color='#eeeeee', linestyle='--', linewidth=0.75)
    if flag_img is not None:
        ax.add_artist(AnnotationBbox(OffsetImage(flag_img, zoom=0.05), (102.5, start_y), frameon=False, box_alignment=(0.5, 0)))

    return fig

# ============================== #
#       INTERFACE LOGIC         #
# ============================== #

# --- Setup week options ---
week_map = {week: f"Week {week}" for week in sorted(df['Week'].unique())}
inv_week_map = {v: k for k, v in week_map.items()}
default_week = max(week_map.keys())

# --- Initialize session state ---
if "selected_week" not in st.session_state:
    st.session_state.selected_week = default_week

# --- Filter data ---
current_week = st.session_state.selected_week
df = df[df["Week"] == current_week]

# --- Headline ---
st.markdown(f"<h1 style='text-align:center; margin-top:-1rem;'>League Tables – Week {current_week}</h1>", unsafe_allow_html=True)

# ============================== #
#       DISPLAY EACH LEAGUE     #
# ============================== #

for league in df['League'].unique():
    st.markdown(f"## {league}")

    selected_label = st.radio(
        label="📅 Select Week",
        options=list(week_map.values()),
        index=list(week_map.keys()).index(st.session_state.selected_week),
        horizontal=True,
        key=f"week_radio_{league}",
        on_change=lambda l=league: st.session_state.update(
            selected_week=inv_week_map[st.session_state[f"week_radio_{l}"]]
        ),
    )

    league_df = df[df["League"] == league]
    fig = plot_league_data(league_df, league, flag_img, start_img, whistle_img)
    st.pyplot(fig)
    plt.close(fig)

# ============================== #
#   FINAL DONATE & ATTRIBUTION  #
# ============================== #

# --- Final donate banner ---
st.markdown("""
    <div style='background-color:#3F1F5A; padding: 1.5rem; border-radius: 1rem; text-align: center; margin-bottom: 2rem;'>
        <h2 style='color: white; margin-bottom: 1rem;'>Please consider donating to Lionheart to support the amazing efforts of our teams!</h2>
        <a href='https://www.justgiving.com/team/sdl-lhh25' target='_blank' style='background-color: #FF6B6B; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 0.5rem; font-weight: bold; font-size: 1.1rem; display: inline-block;'>💖 Donate Now</a>
    </div>
""", unsafe_allow_html=True)

# --- Final credits ---
st.markdown("""
    <div style='display: flex; justify-content: center; align-items: center; margin-top: 1.5rem; margin-bottom: 2.5rem; font-size: 16px; color: #CCCCCC;'>
        <span>Designed by <strong>Kalungi Analytics</strong> · 
            <a href='https://www.linkedin.com/in/ben-sharpe-49659a207/' target='_blank' style='color: #FF6B6B; text-decoration: none; margin-left: 4px;'>
                Connect on LinkedIn
            </a>
        </span>
    </div>
""", unsafe_allow_html=True)
