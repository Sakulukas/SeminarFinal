import requests
import streamlit as st

API_URL = "https://ws.audioscrobbler.com/2.0/"

@st.cache_data(ttl="7d", show_spinner=False) #makes artists only fetched once/wk
def get_artist_info(artist):
    """Return top tags of a certain artist. If API has no info, returns empty list"""
    params = {
        "method" : "artist.gettoptags",
        "artist": artist,
        "api_key": st.secrets["LASTFM_API_KEY"],
        "format": "json",
        "autocorrect": 1, #still finds misspelled names (not if gibberish)
    }
    try: 
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException: #in case api is not reachable
        return []
    if "error" in data: #if for ex. artist isnt found
        return []
    return [tag["name"].lower() for tag in data["toptags"]["tag"][:5]]