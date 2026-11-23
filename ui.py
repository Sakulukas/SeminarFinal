
#ui.py is here to overwrite confi.toml when it comes to sessionstate changes such as the chrsitmas mode I introduce below
#there are also things here concerning little design stuff like the coffee widget --> can be viewed as an add-on where you can
#produce little easter eggs and other fun stuff

#the css tmeplates can be found online as there are many designs available and its rigorous work to do by hand 
import streamlit as st

#Christmas theme ("Alternative 2"), applied as CSS on top of config.toml ── this is done with a css template I found 
XMAS_CSS = """
<style>
/* page + top bar */
.stApp,
header[data-testid="stHeader"] {
    background-color: #DCE0E8 !important;
}
 
/* main text */
.stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li,
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp label,
.stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="stMetricValue"],
.stApp [data-testid="stMetricLabel"] {
    color: #000000 !important;
}
 
/* sidebar: dark red background, light text */
[data-testid="stSidebar"] {
    background-color: #8A2D3A !important;
}
[data-testid="stSidebar"] * {
    color: #F5ECE6 !important;
}
 
/* buttons */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    background-color: #8A2D3A !important;
    color: #FFFFFF !important;
    border: none !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #8A2D3A !important;
    color: #FFFFFF !important;
}
.stButton > button p { color: #FFFFFF !important; }
 
.stApp a { color: #8A2D3A !important; }
</style>
"""
 
# Hover tooltip for the coffee emoji 
TOOLTIP_CSS = """
<style>
.coffee {
    position: relative;
    display: inline-block;
    font-size: 1.6rem;
    line-height: 1;
    cursor: default;
}
.coffee .tip {
    visibility: hidden;
    opacity: 0;
    position: absolute;
    top: 130%;
    right: 0;
    width: 230px;
    padding: 0.6rem 0.8rem;
    border-radius: 0.5rem;
    background: #3B2A20;
    color: #FBF5EC !important;
    font-size: 0.85rem;
    line-height: 1.4;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: opacity 0.2s ease;
    z-index: 1000;
}
.coffee:hover .tip { visibility: visible; opacity: 1; }
</style>
"""
 #used for the windows in analysis, so anything that is registered as st.key-card gets this design
CARD_CSS = """
<style>
[class*="st-key-card_"] {
    background: #8A2D3A
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 16px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
[class*="st-key-card_"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.10);
}
[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; }
 
/* slightly bigger, bolder tabs */
.stTabs [data-baseweb="tab"] p { font-size: 1.05rem; font-weight: 600; }
</style>
"""
 
DEFAULT_COFFEE_TEXT = (
    "Daily tip by (insert name): (random song from one of our playlists). "
)
 
 

def card(name: str):
    """A styled 'window'. Use as:  with card("top_artists"): ..."""
    return st.container(key=f"card_{name}")
 
 
def _init_state() -> None:
    if "xmas" not in st.session_state:
        st.session_state.xmas = False
 
 
def _sync_toggle() -> None:
    # Widget keys are wiped on page change, so it keeps the value in 'xmas' too
    st.session_state.xmas = st.session_state._xmas_toggle
 

def is_xmas() -> bool:
    return st.session_state.get("xmas", False)

def render_header(coffee_text: str = DEFAULT_COFFEE_TEXT) -> None:
    _init_state()
 
    css = TOOLTIP_CSS + CARD_CSS + (XMAS_CSS if is_xmas() else "")
    st.markdown(css, unsafe_allow_html=True)
 
    _, coffee_col, toggle_col = st.columns([10, 1, 2], vertical_alignment="center")
 
    with coffee_col:
        st.markdown(
            f'<div class="coffee">☕<span class="tip">{coffee_text}</span></div>',
            unsafe_allow_html=True,
        )
 
    with toggle_col:
        st.toggle(
            "🎄 Christmas",
            value=st.session_state.xmas,
            key="_xmas_toggle",
            on_change=_sync_toggle,
        )


def style_fig(fig):
    """Make any Plotly figure match the current theme."""
    text = XMAS_CSS["text"] if is_xmas() else AUTUMN["text"]
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",   # transparent → shows the card behind it
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=text,
        colorway=[accent(), "#E8B931", "#5B7B7A", "#9AA0A6"],  # colours for the lines/bars
    )
    return fig