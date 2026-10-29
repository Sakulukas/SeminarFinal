

import streamlit as st

#Christmas theme ("Alternative 2"), applied as CSS on top of config.toml ── this is done with a css template i found 
XMAS_CSS = """
<style>
.stApp { background-color: #006400; }
.stApp, .stApp p, .stApp li, .stApp label,
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { color: #1E3A2F; }

[data-testid="stSidebar"] { background-color: #8B0000; }

.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
    background-color: #A4243B; color: #FFFFFF; border: none;
}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: #7E1B2D; color: #FFFFFF;
}
.stApp a { color: #A4243B; }
</style>
"""

# ── Hover tooltip for the coffee emoji also found with a tmempalte online
TOOLTIP_CSS = """
<style>
.coffee {
    position: relative;
    display: inline-block;
    font-size: 1.6rem;
    cursor: default;
}
.coffee .tip {
    visibility: hidden;
    opacity: 0;
    position: absolute;
    top: 120%;
    right: 0;
    width: 230px;
    padding: 0.6rem 0.8rem;
    border-radius: 0.5rem;
    background: #3B2A20;
    color: #FBF5EC;
    font-size: 0.85rem;
    line-height: 1.4;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: opacity 0.2s ease;
    z-index: 1000;
}
.coffee:hover .tip { visibility: visible; opacity: 1; }
</style>
"""

DEFAULT_COFFEE_TEXT = (
    "Please send some money to +41 xxx so we can afford our gambling addiction"
)


def _init_state() -> None:
    """Create the persistent flag once per browser session."""
    if "xmas" not in st.session_state:
        st.session_state.xmas = False


def _sync_toggle() -> None:
    """Copy the widget's value into the persistent flag.

    Widget keys are wiped when you switch pages, so we keep the real
    value in a separate key ('xmas') that survives page changes.
    """
    st.session_state.xmas = st.session_state._xmas_toggle


def render_header(coffee_text: str = DEFAULT_COFFEE_TEXT) -> None:
    _init_state()
    st.markdown(TOOLTIP_CSS, unsafe_allow_html=True)

    # Wide empty column pushes the two small ones to the right edge
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

    if st.session_state.xmas:
        st.markdown(XMAS_CSS, unsafe_allow_html=True)
