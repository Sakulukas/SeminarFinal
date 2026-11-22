import pandas as pd
import plotly.graph_objects as go


def plot_artist_history(df_plays, selected_artists):
    data = df_plays.copy()

    # Keep local calendar months
    timestamps = pd.to_datetime(data["ts"])

    if timestamps.dt.tz is not None:
        timestamps = timestamps.dt.tz_localize(None)

    data["month"] = timestamps.dt.to_period("M").dt.to_timestamp()

    fig = go.Figure()

    if data.empty:
        fig.add_annotation(
            text="No listening data available.",
            showarrow=False,
        )
        return fig

    # Include every month, including months without plays
    months = pd.date_range(
        data["month"].min(),
        data["month"].max(),
        freq="MS",
    )

    monthly = (
        data.groupby(
            ["master_metadata_album_artist_name", "month"]
        )["sec_played"]
        .sum()
        .div(60)
    )

    for artist in selected_artists:
        if artist not in monthly.index.get_level_values(0):
            continue

        values = monthly.loc[artist].reindex(
            months, fill_value=0
        )

        fig.add_trace(
            go.Scatter(
                x=months,
                y=values,
                name=artist,
                mode="lines",
                line=dict(width=2.5),
                hovertemplate=(
                    "%{x|%b %Y}"
                    "<br>%{y:.1f} minutes"
                    "<extra>%{fullData.name}</extra>"
                ),
            )
        )

    fig.update_layout(
        title="Your Artist Listening History",
        template="plotly_white",
        height=460,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial", size=13, color="#333333"),
        margin=dict(l=70, r=30, t=70, b=100),
        xaxis=dict(
            title="Month",
            showline=True,
            linecolor="#333333",
            showgrid=False,
        ),
        yaxis=dict(
            title="Listening time (minutes)",
            rangemode="tozero",
            showline=True,
            linecolor="#333333",
            gridcolor="#EEEEEE",
        ),
        legend=dict(
            orientation="h",
            y=-0.25,
            x=0,
        ),
        hovermode="x unified",
    )

    return fig