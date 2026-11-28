import streamlit as st
from ui import card, render_header, style_fig





st.set_page_config(
    page_title="Spotifydle",
    page_icon="🎧",
    layout="wide",
)

render_header()

if "plays" not in st.session_state:
    st.warning("Load some data on the home page first.")
    st.stop()

