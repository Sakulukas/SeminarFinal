
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from ui import card, render_header, style_fig
from visualization.plot_top_artists import plot_top_artists
from visualization.plot_heatmap import plot_listening_heatmap
from visualization.plot_artist_history import plot_artist_history

st.set_page_config(page_title="Spotifydle", page_icon="🎧", layout="wide")
render_header()

if "plays" not in st.session_state:
    st.warning("Load some data on the home page first.")
    st.stop()     

plays = st.session_state.plays

col_y, col_m = st.columns(2)
years = sorted(plays["ts"].dt.year.unique())
year = col_y.selectbox("Year", ["All years", *years])
month = col_m.selectbox("Month", ["All months", *range(1, 13)])

data = plays
if year != "All years":
    data = data[data["ts"].dt.year == year]
if month != "All months":
    data = data[data["ts"].dt.month == month] #new columns due to the functions and analysis not having the same syntax

with card("Top_artists"):
    st.plotly_chart(style_fig(plot_top_artists(data)), theme=None)

with card("Heatmap"):
    st.plotly_chart(style_fig(plot_listening_heatmap(data)), theme=None)

with card("artist_hsitory"):
    ranking = plays.groupby("master_metadata_album_artist_name")["sec_played"].sum()
    all_artists = ranking.sort_values(ascending=False).index.tolist()
    chosen = st.multiselect("Pick up to 10 artists", all_artists,
                            default=all_artists[:5], max_selections=10)

    if chosen:
        st.plotly_chart(style_fig(plot_artist_history(plays, chosen)), theme=None)


