from pathlib import Path
from Actual_cleaning import load_audio_data, clean_data

KEEP = [
    "ts", "master_metadata_track_name", "master_metadata_album_artist_name",
    "master_metadata_album_album_name", "sec_played", "play_type",
    "reason_start", "reason_end", "shuffle", "skipped",
]
HERE = Path(__file__).parent  #makes it easier for future references to not always have to type it
OUT = HERE / "examples"

def make_example(name, raw_folder):
    df_raw = load_audio_data(raw_folder)
    df_music, _, _ = clean_data(df_raw)        #keep only df_music that's why there is the ,_,_   
    columns = [c for c in KEEP if c in df_music.columns]
    OUT.mkdir(exist_ok=True)
    df_music[columns].to_csv(OUT / f"{name}.csv", index=False)
    print(f"Saved {name}.csv with {len(df_music):,} rows")

if __name__ == "__main__":
    make_example("Tobias", HERE/ "spotify_files" / "Tobias")   # only my files because all files get merged, so we make three subfolders for each group member
    #make_example("Lukas", HERE/ "spotify_files" / "Lukas")
    #make_example("Niels", HERE/ "spotify_files" / "Niels")