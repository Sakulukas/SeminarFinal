import streamlit as st 
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from ui import render_header


st.set_page_config(page_title="Spotifydle", page_icon="🎧", layout="wide")
render_header()

if st.button("Welcome celebration"):
    st.balloons()

@st.dialog("🎵 Song Recommender")
def recommender_window():
    st.write("Recommendations will go here")

if st.button("Open recommender"):
    recommender_window()

@st.dialog("Celebrity Taste-alike")
def celebrity_window():
    st.write("This celebrity listens to the same music as you!")

if st.button("Reveal the Celebrity"):
    celebrity_window()