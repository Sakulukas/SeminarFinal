"""
Cleaning script for the Spotify project.
 
Safe to run: this script only READS the JSON files. It does not change, move or
delete anything on your computer, and it does not save any files.
 
Step 1: load and merge all audio files (path comes from config.py, not uploaded to GitHub)
Step 2: clean the merged data
"""
 
import json
from pathlib import Path
 
import numpy as np
import pandas as pd
 
try:
    from config import DATA_FOLDER
except ModuleNotFoundError:
    raise SystemExit(
        "config.py not found. Copy config_example.py to config.py (in the same folder "
        "as this script) and enter the path to your Spotify data."
    )
 
name_of_files = "Streaming_History_Audio_*.json"
LOCAL_TZ = "Europe/Zurich"   # local time zone (the export is in UTC)
min_ms_played = 30_000       # agreed: at least 30 seconds = a real play, below = skip
 
 
####### Step 1: load and merge
def load_audio_data(folder=DATA_FOLDER):
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"Data not found: {folder}\nCheck config.py")
 
    files = sorted(folder.glob(name_of_files))
    if not files:
        raise FileNotFoundError(f"No {name_of_files} files in {folder}")
 
    frames = []
    for file in files:
        with open(file, encoding="utf-8") as handle:  # utf-8: special characters (Beyoncé) are read correctly on every system
            frame = pd.DataFrame(json.load(handle))
        print(f"  {file.name}: {len(frame):,} rows")
        frames.append(frame)
 
    df_raw = pd.concat(frames, ignore_index=True)  # stacks the files below each other
    return df_raw
 
 
####### Step 2: clean
def clean_data(df_raw):
    df = df_raw.copy(deep=True)  # preserve the original dataset
 
    #### Remove audiobooks
    # Must happen BEFORE dropping the audiobook columns, because we need them to recognise audiobooks.
    # Older exports may not have these columns at all, so only use the ones that exist.
    audiobook_columns = [c for c in ["audiobook_title", "audiobook_uri", "audiobook_chapter_uri"] if c in df.columns]
    is_audiobook = df[audiobook_columns].notna().any(axis=1) if audiobook_columns else pd.Series(False, index=df.index)
 
    rows_before = len(df)
    df = df.loc[~is_audiobook]
    print("Audiobook rows removed:", rows_before - len(df))
 
    #### Drop columns we do not need
    columns_to_drop = [
        "ip_addr",  # personal data
        "platform",
        "episode_name",
        "episode_show_name",
        "spotify_episode_uri",
        "audiobook_title",
        "audiobook_uri",
        "audiobook_chapter_uri",
        "audiobook_chapter_title",
        "incognito_mode",
    ]
    df = df.drop(columns=columns_to_drop, errors="ignore")  # errors="ignore": no crash if a column is missing in an older export
 
    #### Change time zone
    df["ts"] = pd.to_datetime(df["ts"], utc=True).dt.tz_convert(LOCAL_TZ)  # UTC -> Swiss time
 
    #### Seconds played
    df["sec_played"] = df["ms_played"] / 1000
 
    #### Keep music only (podcasts have no track name)
    is_music = df["master_metadata_track_name"].notna()
    df_music = df.loc[is_music].copy()
    print("Podcast rows (not music, left out of plays/skips):", (~is_music).sum())
 
    #### Remove songs with 0 ms played (technical log entries, never actually heard)
    rows_before = len(df_music)
    df_music = df_music.loc[df_music["ms_played"] > 0].copy()
    print("Songs with 0 ms removed:", rows_before - len(df_music))
 
    #### Sort music into skips (< 30 s) and plays (>= 30 s)
    df_music["play_type"] = np.where(df_music["ms_played"] >= min_ms_played, "play", "skip")
    df_plays = df_music.loc[df_music["play_type"] == "play"].copy()
    df_skips = df_music.loc[df_music["play_type"] == "skip"].copy()
    print("Plays (>= 30 s):", len(df_plays))
    print("Skips (< 30 s):", len(df_skips))
 
    return df_music, df_plays, df_skips
 
 
if __name__ == "__main__":  # only runs when this file is started directly, not when it is imported
    print("Loading audio files:")
    df_raw = load_audio_data()
 
    skipped = sorted(Path(DATA_FOLDER).glob("Streaming_History_Video_*.json"))
    if skipped:
        print("Video files skipped:", [file.name for file in skipped])
 
    print(f"\nTotal: {len(df_raw):,} rows, {df_raw.shape[1]} columns")
    print("Period:", df_raw["ts"].min(), "to", df_raw["ts"].max())
    print("Columns:", list(df_raw.columns))
 
    print("\nCleaning:")
    df_music, df_plays, df_skips = clean_data(df_raw)
    df_music.info()
