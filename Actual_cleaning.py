
#DONT RUN SCRIPT; STILL NEED TO CHECK THAT IT DOES NOT NUKE DATA/PC

import pandas as pd
import numpy as np
from IPython.display import display
from pathlib import Path
from config import DATA_FOLDER #path to Lukas' Spotify Data

#step 1 here later: Path, merge first, then copy in step 2

CWD = Path.cwd('/Users/lukasmaria/SpotifyProject/OldNews/Spotify Extended Streaming History/Streaming_History_Audio_2022.json') #problem with this approach: only works on my personal machine with my personal data
# IN_RAW = 
# figure top part out on weekend

#everything below is step 2:
df_raw = pd.read_json(path) #edit path while doing step 1
df = df_raw.copy(deep=True) #preserve original dataset
#df.info()

####Drop columns mentioned in cleaning.py
df = df.drop(columns=["platform", "ip_addr", "episode_name", "episode_show_name", "spotify_episode_uri", "audiobook_title", "audiobook_uri", "audiobook_chapter_uri", "audiobook_chapter_title", "incognito_mode"])
#split above row into multiple rows, more readable. 

####Changing timezone
LOCAL_TZ = "Europe/Zurich" #define local time zone
df["ts"] = pd.to_datetime(df["ts"], utc=True).dt.tz_convert(LOCAL_TZ) #convert utc to local time zone 

####Changing ms to sec and adding minimum playtime:
min_ms_played = 30000 #agreed upon playtime of 30 seconds, in order for it to be a real play(not a skip, etc.)

rows_before = len(df)
#df = df.loc[df["ms_played"] >= min_ms_played] #this is the actual filter
#df_played = df.loc[df["ms_played"] >= min_ms_played] #IMPORTANT: IF DF = DF.LOC, WILL LOSE SKIPS --> DISCUSS WITH TOBI AND NIELS IF THIS IS RELEVANT (PROBABLY IS)
#print("Short plays removed:", rows_before - len(df_played)) #sanity check, should also be added to report, since might be interesting/good to know that this was deliberate

df["sec_played"] = df["ms_played"] / 1000 #changes ms to seconds
