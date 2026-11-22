import pandas as pd
import plotly.express as px


def plot_top_artists(df_plays):
    # Hörzeit aller Einträge pro Künstler zusammenzählen
    listening_time = (
        df_plays.groupby("master_metadata_album_artist_name")["sec_played"]
        .sum()
        .div(3600)  # Sekunden in Stunden umrechnen
        .nlargest(10)
        .sort_values()
        .reset_index(name="hours")
    )

    # Horizontales Balkendiagramm erstellen
    fig = px.bar(
        listening_time,
        x="hours",
        y="master_metadata_album_artist_name",
        orientation="h",
        title="Deine Top 10 Künstler nach Hörzeit",
        labels={
            "hours": "Hörzeit in Stunden",
            "master_metadata_album_artist_name": "Künstler",
        },
    )

    return fig


# Dieser Teil läuft nur, wenn du diese Datei direkt startest.
if __name__ == "__main__":
    # Erfundenes Beispiel im Format eurer bereinigten Daten
    example_data = pd.DataFrame({
        "master_metadata_album_artist_name": [
            "Drake", "Adele", "Coldplay", "Drake",
            "Adele", "ABBA", "Coldplay", "Eminem",
        ],
        "sec_played": [
            180, 240, 210, 200,
            180, 300, 240, 190,
        ],
    })

    fig = plot_top_artists(example_data)
    fig.write_html("top_artists.html", auto_open=True)