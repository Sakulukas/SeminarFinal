import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from ui import card, render_header
import streamlit as st 

#the goal of this page is the creation of a 3d space that is similar to a probability density cloud (see electron3d.py on github repo). Each song gets a rating in the
#three categories and will then get a vector attached that. the coordinates of your songs will show you trends in your song choices as well as 
#show you songs thta are similar to it. This will be done by estimating the euklidian distance between songs 

st.set_page_config(page_title="Song Space", page_icon= "🌌", layout="wide")
render_header()

DIM =["arousal", "valence", "depth"] #three dimensions that every song can be categorized in as per digitalmusicnews

@st.cache_data
def load_demo_songs(n: int = 150) -> pd.DataFrame:
    """Random songs so you can test the plot before the real data exists.""" #just here to test some stuff out before real data comes
    rng = np.random.default_rng(7)
    return pd.DataFrame(
        {
            "song": [f"Song {i}" for i in range(n)],
            "artist": rng.choice([f"Artist {c}" for c in "ABCDEF"], n),
            "arousal": rng.uniform(1, 10, n).round(1),
            "valence": rng.uniform(1, 10, n).round(1),
            "depth": rng.uniform(1, 10, n).round(1),
        }
    )


songs = st.session_state.get("songs", load_demo_songs()) #this will be changed later on to be the real data set 

#this is the ssimiong finder using 
def find_similar(df: pd.DataFrame, song: str, k: int = 5) -> pd.DataFrame:
    """The k songs closest to `song` in 3D space (Euclidean distance)."""
    target = df.loc[df["song"] == song, DIM].to_numpy()        # shape (1, 3)
    distances = np.linalg.norm(df[DIM].to_numpy() - target, axis=1)
    return (
        df.assign(distance=distances.round(2))
        .query("song != @song")                                 # not itself
        .nsmallest(k, "distance")
    )


st.title("Your Song Space")
st.caption("3D coordinate system, where every dot is a song and similar songs are close to each other")

controls_col, plot_col = st.columns([1, 3]) #create columns
 
with controls_col, card("controls"):
    selected = st.selectbox("Pick a song", songs["song"])
    k = st.slider("How many similar songs?", 1, 10, 5)
    #show_cloud = st.toggle("Show density cloud") #this is a later idea that I haven't done the function to yet 

similar = find_similar(songs, selected, k)
selected_row = songs[songs["song"] == selected]


#this is the skeleton where every function is defined, but now these functions have to be created in a figure on streamlit

fig = go.Figure()

fig.add_trace(go.Scatter3d(
    x=songs["arousal"], y=songs["valence"], z=songs["depth"],
    mode="markers",
    marker=dict(size=4, color="#9AA0A6", opacity=0.5),
    text=songs["song"] + " – " + songs["artist"],
    hovertemplate="%{text}<br>Arousal %{x} · Valence %{y} · Depth %{z}<extra></extra>",
    name="All songs",
)) #adds songs to the figure and the hovertemplate command will show song name and artist when you hover over a dot

fig.add_trace(go.Scatter3d(
    x=similar["arousal"], y=similar["valence"], z=similar["depth"],
    mode="markers",
    marker=dict(size=7, color="#ea5a4f"),
    text=similar["song"] + " – " + similar["artist"],
    hovertemplate="%{text}<extra>similar</extra>",
    name="Similar",
)) #this will show the songs deemed similar according to the euclidian distance

fig.add_trace(go.Scatter3d(
    x=selected_row["arousal"], y=selected_row["valence"], z=selected_row["depth"],
    mode="markers",
    marker=dict(size=11, color="#E8B931", symbol="diamond"),
    text=selected_row["song"] + " – " + selected_row["artist"],
    hovertemplate="%{text}<extra>selected</extra>",
    name="Selected",
)) #this will show the selected song and will make it differ from the others (colour etc.)

axis = dict(range=[1, 10]) #range of DIM is 1 to 10
fig.update_layout(
    scene=dict(
        xaxis=dict(title="Arousal", **axis), #these rows name the different axes 
        yaxis=dict(title="Valence", **axis),
        zaxis=dict(title="Depth", **axis),
    ),
    height=650,
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="rgba(0,0,0,0)",   #this makes it transparent so that my theme can overwrite it 
    legend=dict(orientation="h", y=1.02),
)

#the following lines make it so that it follows the same scheme as the other pages on the website
with plot_col, card("plot"):
    st.plotly_chart(fig, use_container_width=True) 
 
with card("similar_table"):
    st.subheader(f"Songs similar to {selected}")
    st.dataframe(similar[["song", "artist", "distance", *DIM]], hide_index=True)