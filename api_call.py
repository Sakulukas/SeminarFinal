import requests
import streamlit as st

API_URL = "https://ws.audioscrobbler.com/2.0/"

@st.cache_data(ttl="7d", show_spinner=False) #makes artists only fetched once/wk
def get_artist_info(artist):
    """Return top tags of a certain artist. If API has no info, returns empty list"""
    para = {
        "method" : "artist.gettoptags",
        "artist": artist
        "api_key": st.secrets["LASTFM_API_KEY"],
        "format": "json"
        "autocorrect": 1 #still finds misspelled names (not if gibberish)
    }