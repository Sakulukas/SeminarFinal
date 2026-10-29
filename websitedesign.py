import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ui import render_header


st.set_page_config(page_title="Spotifydle", page_icon="🎧", layout="wide")
render_header()

st.title("Spotifydle")
st.write("""Find out everything about your music taste on one website""")

custom_json_file = st.file_uploader("Upload your JSON Spotify file here:") #here users can upload their JSON files

st.write("""Otherwise use our predownloaded files for to access a limited amount of features""") #alternative when people don't want to shrae their data
#we'll let them access certain features like song recommendation, quizes etc. but we cannot analyse their music habits



