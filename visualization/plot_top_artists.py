import plotly.express as px

def plot_top_artists(df_plays):
    # Calculate total listening time per artist in minutes
    listening_time = (
        df_plays.groupby("master_metadata_album_artist_name")["sec_played"]
        .sum()
        .div(60)
        .nlargest(10)
        .sort_values()
        .reset_index(name="minutes")
    )

    fig = px.bar(
        listening_time,
        x="minutes",
        y="master_metadata_album_artist_name",
        color="master_metadata_album_artist_name",
        color_discrete_sequence=px.colors.qualitative.Plotly,
        orientation="h",
        title="Your Top 10 Artists by Listening Time",
        labels={
            "minutes": "Listening time (minutes)",
            "master_metadata_album_artist_name": "Artist",
        },
        template="plotly_white",
    )

    fig.update_layout(
        width=750,
        height=450,
        bargap=0.55,
        showlegend=False,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial", size=13, color="#333333"),
        margin=dict(l=120, r=30, t=60, b=50),
        yaxis=dict(
            categoryorder="array",
            categoryarray=list(
                listening_time["master_metadata_album_artist_name"]
            ),
            title=None,
        ),
        xaxis=dict(
            title="Listening time (minutes)",
            gridcolor="#EEEEEE",
            zeroline=False,
        ),
    )

    fig.update_traces(
        marker_line_width=0,
        hovertemplate=(
            "%{y}<br>Listening time: %{x:.1f} minutes<extra></extra>"
        ),
    )
    fig.update_xaxes(
        showline=True,
        linecolor="#333333",
        linewidth=1,
        ticks="outside",
    )

    fig.update_yaxes(
        showline=True,
        linecolor="#333333",
        linewidth=1,
        ticks="outside",
    )

    return fig
