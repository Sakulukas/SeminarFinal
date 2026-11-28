import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ui import render_header
from pathlib import Path
from Actual_cleaning import clean_data
from data_loading import split_plays_skips, from_example, from_uploads
import json


st.set_page_config(page_title="Spotifydle", page_icon="🎧", layout="wide")
render_header()

st.title("Spotifydle")
st.write("""Find out everything about your music taste on one website""")


example_dir = Path(__file__).parent/"examples"
examples = {p.stem: p for p in example_dir.glob("*.csv")}
source = st.radio("Which data do you want to explore?",
                  ["Try our example data", "Upload your own"], horizontal=True)

df_music = None
if source == "Upload your own":
    uploaded = st.file_uploader("Your Spotify JSON files", type="json", accept_multiple_files=True)
    if uploaded:
        df_music = from_uploads(uploaded) #see data_loading -> from_uploads uses data cleaning function
else: 
    choice = st.selectbox("Pick one of ours", list(examples))
    df_music = from_example(examples[choice])

if df_music is not None:
    st.session_state.df = df_music
    st.session_state.plays, st.session_state.skips = split_plays_skips(df_music)
    st.success("Data loaded and ready to go!")

    







st.write("""Otherwise use our predownloaded files for to access a limited amount of features""") #alternative when people don't want to shrae their data
#we'll let them access certain features like song recommendation, quizes etc. but we cannot analyse their music habits



