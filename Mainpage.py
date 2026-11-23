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


example_dir = Path(__file__).parent/"example"
examples = {p.stem: p for p in example_dir.glob("*.json")}
source = st.radio("Which data do you want to explore?",
                  ["Try our example data", "Upload your own"], horizontal=True)

raw = True
if source == "Upload your own":
    uploaded = st.file_uploader("Upload your JSON Spotify file here:") #here users can upload their JSON files
    if uploaded:
        raw = json.load(uploaded)
else: 
    choice = st.selectbox("Pick one of ours", list(examples))
    raw = json.loads(examples[choice].read_text())

if raw is not None and st.button("Use this button"):
    st.session_state.df = raw
    #will in future be clean_data(raw)
    st.success("Data loaded and ready to go!")

    







st.write("""Otherwise use our predownloaded files for to access a limited amount of features""") #alternative when people don't want to shrae their data
#we'll let them access certain features like song recommendation, quizes etc. but we cannot analyse their music habits



