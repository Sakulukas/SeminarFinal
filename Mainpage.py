import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ui import render_header
from pathlib import Path
from Actual_cleaning import clean_data
import json


st.set_page_config(page_title="Spotifydle", page_icon="🎧", layout="wide")
render_header()

st.title("Spotifydle")
st.write("""Find out everything about your music taste on one website""")


example_dir = Path(__file__).parent/"spotify_files"
examples = {p.stem: p for p in example_dir.glob("*.json")}
source = st.radio("Which data do you want to explore?",
                  ["Try our example data", "Upload your own"], horizontal=True)

raw = True
if source == "Upload your own":
    uploaded = st.file_uploader("Your Spotify JSON files", type="json", accept_multiple_files=True)
    if uploaded:
        raw = [row for f in uploaded for row in json.load(f)]
else: 
    choice = st.selectbox("Pick one of ours", list(examples))
    raw = json.loads(examples[choice].read_text())

if raw is not None and st.button("Use this button"):
    df_raw = pd.DataFrame(raw)
    df_music, df_plays, df_skips = clean_data(df_raw)
    st.session_state.df = df_music
    st.session_state.plays = df_plays
    st.session_state.skips = df_skips
    st.success("Data loaded and ready to go!")

    







st.write("""Otherwise use our predownloaded files for to access a limited amount of features""") #alternative when people don't want to shrae their data
#we'll let them access certain features like song recommendation, quizes etc. but we cannot analyse their music habits



