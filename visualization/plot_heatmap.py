import json
from pathlib import Path
import pandas as pd
import plotly.express as px


     
def plot_listening_heatmap(df_plays):
    data = df_plays.copy()
    data["ts"] = pd.to_datetime(data["ts"])

    data["weekday"] = data["ts"].dt.dayofweek
    data["hour"] = data["ts"].dt.hour

    listening_time = (
        data.groupby(["weekday", "hour"])["sec_played"]
        .sum()
        .div(60)
        .unstack(fill_value=0)
        .reindex(index=range(7), columns=range(24), fill_value=0)
    )

    fig = px.imshow(
        listening_time,
        x=list(range(24)),
        y=[
            "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday",
        ],
        labels={
            "x": "Hour of day",
            "y": "Day of week",
            "color": "Minutes",
        },
        title="Your Weekly Listening Pattern",
        color_continuous_scale=[
            "#F3F6FA",
            "#D6E4F0",
            "#8DBADB",
            "#468BC0",
            "#185A91",
        ],
        zmin=0,
        aspect="equal",
        template="plotly_white",
    )

    fig.update_layout(
        width=1050,
        height=440,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial", size=13, color="#333333"),
        title=dict(x=0.5, xanchor="center"),
        margin=dict(l=110, r=110, t=80, b=70),
        coloraxis_colorbar=dict(
            title="Minutes",
            thickness=14,
            len=0.85,
        ),
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=list(range(24)),
        ticktext=[f"{hour:02d}" for hour in range(24)],
        side="bottom",
        title="Hour of day",
        showgrid=False,
        zeroline=False,
        ticks="",
    )

    fig.update_yaxes(
        title=None,
        showgrid=False,
        zeroline=False,
        ticks="",
    )

    # Separate the cells with small white gaps
    fig.update_traces(
        xgap=0,
        ygap=0,
        hovertemplate=(
            "%{y}, %{x}:00–%{x}:59"
            "<br>Listening time: %{z:.1f} minutes"
            "<extra></extra>"
        ),
    )

    return fig
