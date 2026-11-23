import streamlit as st 
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from ui import render_header, style_fig
#from visualization.plot_artist_history import plot_artist_history
#from visualization.plot_heatmap import plot_listening_heatmap
#from visualization.plot_skip_rates import render_skip_rates
#from visualization.plot_top_artists import plot_top_artists
from visualization.preview_plots import load_spotify_data

st.set_page_config(page_title="Spotifydle", page_icon="🎧", layout="wide")
render_header()

load_spotify_data(st.session_state.df)

