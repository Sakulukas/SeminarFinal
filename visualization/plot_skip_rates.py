import json


def render_skip_rates(df_music):
    data = df_music.loc[
        df_music["sec_played"] > 0
    ].copy()

    data["year"] = data["ts"].dt.year
    data["month"] = data["ts"].dt.month

    # Aggregate counts without including IP addresses or exact timestamps
    grouped = (
        data.groupby([
            "year",
            "month",
            "master_metadata_album_artist_name",
            "sec_played",
        ])
        .size()
        .reset_index(name="count")
    )

    payload = {
        "years": sorted(data["year"].unique().tolist()),
        "rows": grouped.values.tolist(),
    }

    safe_json = (
        json.dumps(payload, ensure_ascii=True, allow_nan=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )

    return """
    <section class="chart">
        <h2>Skip Rates by Artist</h2>

        <p>
            A skip is a listening entry shorter than your chosen
            threshold. Zero-second entries are excluded.
            Only artists with at least 20 entries in the selected
            period are shown.
        </p>

        <div class="skip-controls">
            <label>
                Year
                <select id="skip-year"></select>
            </label>

            <label>
                Month
                <select id="skip-month"></select>
            </label>

            <label>
                Skip threshold (seconds)
                <input
                    id="skip-threshold"
                    type="number"
                    min="1"
                    step="1"
                    value="30"
                >
            </label>
        </div>

        <p id="skip-message" aria-live="polite"></p>
        <div id="skip-chart"></div>
    </section>

    <style>
        .skip-controls {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin: 20px 0;
        }

        .skip-controls label {
            display: flex;
            flex-direction: column;
            gap: 8px;
            font-size: 14px;
        }

        .skip-controls select,
        .skip-controls input {
            padding: 10px 12px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            background: white;
            color: #243247;
            font: inherit;
        }

        #skip-threshold {
            width: 150px;
        }

        #skip-message {
            color: #64748b;
        }
    </style>

    <script id="skip-data" type="application/json">
        __SKIP_DATA__
    </script>

    <script>
    (() => {
        const payload = JSON.parse(
            document.getElementById("skip-data").textContent
        );

        const year = document.getElementById("skip-year");
        const month = document.getElementById("skip-month");
        const threshold = document.getElementById("skip-threshold");
        const message = document.getElementById("skip-message");

        const months = [
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ];

        year.add(new Option("All years", "all"));

        payload.years.forEach(value => {
            year.add(new Option(value, String(value)));
        });

        month.add(new Option("All months", "all"));

        months.forEach((name, index) => {
            month.add(new Option(name, String(index + 1)));
        });

        function updateChart() {
            const limit = Number(threshold.value);

            if (
                threshold.value.trim() === "" ||
                !Number.isFinite(limit) ||
                limit < 1 ||
                !Number.isInteger(limit)
            ) {
                message.textContent =
                    "Enter a whole number of at least 1 second.";
                return;
            }

            const totals = new Map();

            payload.rows.forEach(row => {
                const [
                    rowYear, rowMonth, artist, seconds, count
                ] = row;

                if (
                    year.value !== "all" &&
                    rowYear !== Number(year.value)
                ) return;

                if (
                    month.value !== "all" &&
                    rowMonth !== Number(month.value)
                ) return;

                if (!totals.has(artist)) {
                    totals.set(artist, {
                        artist: artist,
                        entries: 0,
                        skips: 0
                    });
                }

                const item = totals.get(artist);

                item.entries += count;

                if (seconds < limit) {
                    item.skips += count;
                }
            });

            const top = [...totals.values()]
                .filter(item => item.entries >= 20)
                .map(item => ({
                    ...item,
                    rate: item.skips / item.entries * 100
                }))
                .sort((a, b) =>
                    b.rate - a.rate ||
                    b.entries - a.entries ||
                    a.artist.localeCompare(b.artist)
                )
                .slice(0, 10)
                .reverse();

            message.textContent = top.length === 0
                ? "No artists have at least 20 entries in this period."
                : "Showing up to 10 artists with the highest skip rates.";

            const colors = [
                "#636EFA", "#EF553B", "#00CC96", "#AB63FA",
                "#FFA15A", "#19D3F3", "#FF6692", "#B6E880",
                "#FF97FF", "#FECB52"
            ];

            const selectedMonth =
                month.options[month.selectedIndex].text;

            const selectedYear =
                year.options[year.selectedIndex].text;

            Plotly.react(
                "skip-chart",
                [{
                    type: "bar",
                    orientation: "h",
                    x: top.map(item => item.rate),
                    y: top.map(item => item.artist),
                    marker: {
                        color: top.map((item, index) => colors[index]),
                        line: {width: 0}
                    },
                    customdata: top.map(item => [
                        item.skips,
                        item.entries,
                        item.entries - item.skips
                    ]),
                    hovertemplate:
                        "%{y}<br>" +
                        "Skip rate: %{x:.1f}%<br>" +
                        "Skips: %{customdata[0]}<br>" +
                        "Plays: %{customdata[2]}<br>" +
                        "Total entries: %{customdata[1]}" +
                        "<extra></extra>"
                }],
                {
                    title: {
                        text:
                            "Skip Rates by Artist" +
                            "<br><sup>Threshold: " + limit +
                            " seconds · " + selectedMonth +
                            " · " + selectedYear + "</sup>"
                    },
                    height: 500,
                    autosize: true,
                    bargap: 0.55,
                    showlegend: false,
                    paper_bgcolor: "white",
                    plot_bgcolor: "white",
                    font: {
                        family: "Arial",
                        size: 13,
                        color: "#333333"
                    },
                    margin: {l: 120, r: 40, t: 90, b: 60},
                    xaxis: {
                        title: {text: "Skip rate (%)"},
                        range: [0, 100],
                        ticksuffix: "%",
                        showline: true,
                        linecolor: "#333333",
                        gridcolor: "#EEEEEE",
                        zeroline: false
                    },
                    yaxis: {
                        automargin: true,
                        showline: true,
                        linecolor: "#333333",
                        categoryorder: "array",
                        categoryarray: top.map(item => item.artist)
                    },
                    annotations: top.length === 0 ? [{
                        text: "No qualifying artists in this period.",
                        x: 0.5,
                        y: 0.5,
                        xref: "paper",
                        yref: "paper",
                        showarrow: false
                    }] : []
                },
                {
                    responsive: true,
                    displaylogo: false
                }
            );
        }

        year.addEventListener("change", updateChart);
        month.addEventListener("change", updateChart);
        threshold.addEventListener("input", updateChart);

        updateChart();
    })();
    </script>
    """.replace("__SKIP_DATA__", safe_json)


# Native Python/Plotly API for Streamlit.
def skip_rate_data(df_music, threshold=30, year=None, month=None):
    import math
    from visualization.analysis_data import ARTIST, prepare_music, filter_period
    if not math.isfinite(float(threshold)) or float(threshold) < 1:
        raise ValueError('Skip threshold must be at least one second.')
    data = filter_period(prepare_music(df_music), year, month)
    data['is_skip'] = data['sec_played'].lt(float(threshold))
    totals = data.groupby(ARTIST)['is_skip'].agg(entries='size', skips='sum').reset_index()
    totals = totals.loc[totals['entries'].ge(20)].copy()
    totals['plays'] = totals['entries'] - totals['skips']
    totals['skip_rate'] = totals['skips']/totals['entries']*100
    return totals.sort_values(['skip_rate','entries',ARTIST], ascending=[False,False,True]).head(10)


def plot_skip_rates(df_music, threshold=30, year=None, month=None):
    import plotly.express as px
    from visualization.analysis_data import ARTIST, empty_figure
    data = skip_rate_data(df_music, threshold, year, month).iloc[::-1]
    if data.empty:
        return empty_figure('Skip Rates by Artist', 'No artists have at least 20 entries in this period.')
    fig = px.bar(data, x='skip_rate', y=ARTIST, color=ARTIST, orientation='h',
        color_discrete_sequence=px.colors.qualitative.Plotly, template='plotly_white',
        custom_data=['skips','plays','entries'], labels={'skip_rate':'Skip rate (%)',ARTIST:''},
        title=f'Skip Rates by Artist · threshold: {threshold:g} seconds')
    fig.update_layout(height=500,bargap=.55,showlegend=False,paper_bgcolor='white',plot_bgcolor='white')
    fig.update_xaxes(range=[0,100],ticksuffix='%')
    fig.update_yaxes(categoryorder='array',categoryarray=data[ARTIST].tolist(),automargin=True)
    fig.update_traces(hovertemplate='%{y}<br>Skip rate: %{x:.1f}%<br>Skips: %{customdata[0]}<br>Plays: %{customdata[1]}<br>Total: %{customdata[2]}<extra></extra>')
    return fig
