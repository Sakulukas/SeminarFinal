from Actual_cleaning import clean_data, load_audio_data
import json
import pandas as pd

def from_uploads(files) -> pd.DataFrame:  #takes uploaded json file adn turns them into ac leaned version df_musich 
    rows = [row for f in files for row in json.load(f)] #creates rows instead of files for the analysis part
    df_music, _, _ = clean_data(pd.DataFrame(rows))
    return df_music

def from_example(path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["ts"] = pd.to_datetime(df["ts"], utc = True).dt.tz_convert("Europe/Zurich") #the current ts is just text so we have to convert it back to actual time 
    return df

def split_plays_skips(df_music): #have to split some functions of for future use in analysis
    plays = df_music[df_music["play_type"] == "play"]
    skips = df_music[df_music["play_type"] == "skip"]
    return plays, skips



