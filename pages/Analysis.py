import streamlit as st
from ui import card, render_header, style_fig
from visualization.streamlit_dashboard import render_analysis


st.set_page_config(
    page_title="Analysis",
    page_icon="🕵️",
    layout="wide",
)

render_header()

if "plays" not in st.session_state:
    st.warning("Load some data on the home page first.")
    st.stop()

render_analysis(
    st.session_state.plays,
    df_music = st.session_state.df,
    style_figure= style_fig,
    card_factory=card,
    )
