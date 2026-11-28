"""Shared preparation for native Plotly figures and Streamlit controls."""
import math
import pandas as pd

ARTIST = 'master_metadata_album_artist_name'
TZ = 'Europe/Zurich'


def prepare_music(frame, plays_only=False):
    data = frame[['ts', ARTIST, 'sec_played']].copy()
    times = pd.to_datetime(data['ts'], errors='coerce')
    # Cleaned input uses Swiss time. Treat naive timestamps as Swiss local time.
    if times.dt.tz is None:
        times = times.dt.tz_localize(TZ, ambiguous='NaT', nonexistent='NaT')
    else:
        times = times.dt.tz_convert(TZ)
    data['ts'] = times
    data['sec_played'] = pd.to_numeric(data['sec_played'], errors='coerce')
    data = data.dropna(subset=['ts', ARTIST, 'sec_played'])
    data = data.loc[data['sec_played'].map(math.isfinite)]
    cutoff = data['sec_played'].ge(30) if plays_only else data['sec_played'].gt(0)
    return data.loc[cutoff].sort_values('ts').reset_index(drop=True)


def filter_period(data, year=None, month=None, column='ts'):
    mask = pd.Series(True, index=data.index)
    if year is not None:
        mask &= data[column].dt.year.eq(int(year))
    if month is not None:
        mask &= data[column].dt.month.eq(int(month))
    return data.loc[mask].copy()


def search_artists(artists, query):
    query = query.strip().casefold()
    return sorted(
        (name for name in artists if query in name.casefold()),
        key=lambda name: (not name.casefold().startswith(query), name.casefold()),
    )


def empty_figure(title, message):
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.update_layout(title=title, template='plotly_white', height=450)
    fig.add_annotation(text=message, x=.5, y=.5, xref='paper', yref='paper', showarrow=False)
    return fig
