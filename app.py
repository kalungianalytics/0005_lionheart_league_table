import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import font_manager
import streamlit as st
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# --- Load and set custom font globally ---
font_path = "NotoSans-VariableFont_wdth,wght.ttf"
font_prop = font_manager.FontProperties(fname=font_path)
mpl.rcParams['font.family'] = font_prop.get_name()

# --- Streamlit page config ---
st.set_page_config(page_title="Lionheart 2025 HQ Hop League Tables", layout="wide")

# --- Custom CSS for dark theme and fonts ---
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

# --- Optional: Increase radio button text size for testing ---
st.markdown("""
    <style>
        /* Increase font size of radio button labels */
        div[data-baseweb="radio"] > div {
            font-size: 1.15rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Credits bar ---
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

st.image("logo.png", use_container_width=True)

# --- Donate banner ---
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

# --- Caching data load ---
@st.cache_data(show_spinner=False)
def load_data():
    return pd.read_csv("data.csv")

# --- Caching image load ---
@st.cache_resource(show_spinner=False)
def load_image(path):
    return mpimg.imread(path)

# --- Cache loading league-specific runner images ---
#@st.cache_resource(show_spinner=False)
def load_league_images(league_number):
    folder_path = os.path.join("images", str(league_number))
    if not os.path.exists(folder_path):
        return []
    image_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".png")])
    images = [mpimg.imread(os.path.join(folder_path, f)) for f in image_files]
    return images

# --- Load data and images once ---
df = load_data()
flag_img = load_image("checkered_flag.png")
start_img = load_image("start_icon.png")
whistle_img = load_image("whistle.png")

# Map League to League Number (for folder)
league_to_number = df.drop_duplicates(subset=['League'])[['League', 'League Number']].set_index('League')['League Number'].to_dict()

# --- Plotting function ---
def plot_league_data(league_df, league_name, flag_img, start_img, whistle_img):
    df_sorted = league_df.sort_values(by="% Distance Covered").reset_index(drop=True)
    league_number = league_to_number.get(league_name, 1)
    runner_images = load_league_images(league_number)
    
    if not runner_images or df_sorted.empty:
        return plt.figure()

    max_bars = 20
    num_bars = min(len(df_sorted), max_bars)

    fig, ax = plt.subplots(figsize=(14, 0.65 * num_bars))
    #fig, ax = plt.subplots(figsize=(10, 0.4 * num_bars))
    fig.patch.set_facecolor('#171717')
    ax.set_facecolor('#171717')
    ax.axis('off')

    bar_height = 0.7
    y_positions = range(num_bars)

    ax.barh(y=y_positions, width=df_sorted['% Distance Covered'][:num_bars], height=bar_height, color=(0,0,0,0))

    # Add runner icons, alternating
    for i, value in enumerate(df_sorted['% Distance Covered'][:num_bars]):
        img = runner_images[i % len(runner_images)]
        icon = OffsetImage(img, zoom=0.05, resample=True)
        ab = AnnotationBbox(icon, (value, i), frameon=False, box_alignment=(0.5, 0.5))
        ax.add_artist(ab)

    # Labels on left and right of bars
    for i, (value, name) in enumerate(zip(df_sorted['% Distance Covered'][:num_bars], df_sorted['Team Name'][:num_bars])):
        ax.text(x=value - 2.5, y=i, s=name, ha='right', va='center',
                fontsize=16, color='white', weight='bold', fontproperties=font_prop)
        label_text = "" if value == 0 else f"{value:.1f}%"
        if value >= 100:
            label_color = '#80CFA9'   # Green
        elif value >= 85:
            label_color = '#FFD700'   # Gold
        else:
            label_color = '#FF6B6B'   # Red
        ax.text(x=value + 4.5, y=i, s=label_text, ha='left', va='center',
                fontsize=14, color=label_color, fontproperties=font_prop)


    #ax.set_xlim(0, 110)
    max_value = df_sorted['% Distance Covered'][:num_bars].max()
    buffer = 5  # Adjust as needed
    ax.set_xlim(0, max(110, max_value + buffer))

    ax.set_ylim(-1, y_positions[-1] + 1.2)

    # Start line & whistle icon
    start_y = num_bars - 0.5 + 0.2
    ax.axvline(x=0, color='#eeeeee', linestyle='--', linewidth=0.75)
    start_icon = OffsetImage(whistle_img, zoom=0.05)
    ab_start = AnnotationBbox(start_icon, (0, start_y), frameon=False, box_alignment=(0.5, 0))
    ax.add_artist(ab_start)

    # Finish line & checkered flag icon
    ax.axvline(x=100, color='#eeeeee', linestyle='--', linewidth=0.75)
    flag_icon = OffsetImage(flag_img, zoom=0.05)
    ab_flag = AnnotationBbox(flag_icon, (102.5, start_y), frameon=False, box_alignment=(0.5, 0))
    ax.add_artist(ab_flag)

    return fig


# --- Week selection radio buttons ---
week_map = {week: f"Week {week}" for week in sorted(df['Week'].unique())}
inv_week_map = {v: k for k, v in week_map.items()}
default_week = max(week_map.keys())  # Auto-select latest week

# --- Week selection heading (tight spacing) ---
st.markdown(
    """
    <div style='
        font-size:1.4rem;
        font-weight:bold;
        color:#FFFFFF;
        margin-bottom:0.2rem;
        line-height:0.5;
    '>📅 Select Week</div>
    """,
    unsafe_allow_html=True
)

# --- Radio buttons (label hidden for no extra space) ---
selected_label = st.radio(
    label="",  # Empty label avoids double spacing
    options=list(week_map.values()),
    index=list(week_map.values()).index(f"Week {default_week}"),
    horizontal=True,
)

selected_week = inv_week_map[selected_label]
df = df[df['Week'] == selected_week]

# --- Update headline text ---
st.markdown(f"""
    <h1 style='text-align:center; margin-top:-1rem;'>League Tables – {selected_label}</h1>
""", unsafe_allow_html=True)

# --- Display league tables ---
for league in df['League'].unique():
    st.markdown(f"## {league}")
    league_df = df[df['League'] == league]
    fig = plot_league_data(league_df, league, flag_img, start_img, whistle_img)
    st.pyplot(fig)
    plt.close(fig)
