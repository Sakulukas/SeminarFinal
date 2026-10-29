import pandas as pd
import numpy as np
from IPython.display import display
from pathlib import Path

#step 1 here later: Path, merge first, then copy in step 2

CWD = Path.cwd('/Users/lukasmaria/SpotifyProject/OldNews/Spotify Extended Streaming History/Streaming_History_Audio_2022.json') #problem with this approach: only works on my personal machine with my personal data


#everything below is step 2:
df_raw = pd.read_json(path) #edit path while doing step 1
df = df_raw.copy(deep=True) #preserve original dataset
#df.info()
