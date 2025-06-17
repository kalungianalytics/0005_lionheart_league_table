import os
import pandas as pd
import streamlit as st
import altair as alt

# --- Page Config ---
st.set_page_config(page_title="Lionheart 2025 HQ Hop League Tables", layout="wide")

# --- CSS Styling ---
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
        h1, h2, h3, h4, h5, h6, p, span, div {{
            color: white !important;
        }}
        [data-testid="stSidebar"] {{
            background-color: #1e1e1e !important;
        }}
        button {{
            background-color: #3F1F5A !important;
            color: white !important;
        }}
    </style>
""", unsafe_allow_html=True)

# --- Header and Branding ---
st.image("logo.jpg", use_container_width=True)

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
        '>💖 Donate Now</a>
    </div>
""", unsafe_allow_html=True)

# --- Load and Cache Data ---
@st.cache_data(show_spinner=False)
def load_data():
    return pd.read_csv("data.csv")

df = load_data()

# --- Display League Tables ---
for league in df['League'].unique():
    st.markdown(f"## {league}")
    league_df = df[df['League'] == league].copy()
    league_df = league_df.sort_values(by="% Distance Covered").tail(20)

    # Altair chart
    chart = alt.Chart(league_df).mark_bar(size=25).encode(
        x=alt.X('% Distance Covered:Q', scale=alt.Scale(domain=[0, 110]), title="% Distance Covered"),
        y=alt.Y('Team Name:N', sort='-x', title=""),
        color=alt.value("#FF6B6B"),
        tooltip=["Team Name", "% Distance Covered"]
    ).properties(
        height=30 * len(league_df),
        width=800,
        background="#171717"
    ).configure_axis(
        labelColor='white',
        titleColor='white'
    ).configure_view(
        strokeWidth=0
    ).configure_mark(
        opacity=1
    )

    st.altair_chart(chart, use_container_width=True)
