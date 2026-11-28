import json
import pandas as pd


ARTIST = "master_metadata_album_artist_name"


def render_discovery(df_plays):
    data = df_plays[["ts", ARTIST, "sec_played"]].copy()

    data["ts"] = pd.to_datetime(
        data["ts"], utc=True, errors="coerce"
    ).dt.tz_convert("Europe/Zurich")

    data["sec_played"] = pd.to_numeric(
        data["sec_played"], errors="coerce"
    )

    data = data.dropna(subset=["ts", ARTIST, "sec_played"])
    data = data.loc[data["sec_played"] >= 30].copy()
    data["month"] = data["ts"].dt.strftime("%Y-%m")

    # First appearances always use the complete history
    first = data.groupby(ARTIST)["ts"].min()

    monthly = (
        data.groupby(["month", ARTIST])["sec_played"]
        .sum()
        .div(60)
        .reset_index(name="minutes")
    )

    records = [
        [
            row["month"],
            row[ARTIST],
            float(row["minutes"]),
            row["month"] == first[row[ARTIST]].strftime("%Y-%m"),
        ]
        for _, row in monthly.iterrows()
    ]

    artists = [
        [
            name,
            timestamp.strftime("%Y-%m"),
            timestamp.strftime("%d %b %Y, %H:%M"),
        ]
        for name, timestamp in first.items()
    ]

    periods = []

    if not data.empty:
        periods = pd.period_range(
            data["month"].min(),
            data["month"].max(),
            freq="M",
        ).astype(str).tolist()

    payload = {
        "records": records,
        "artists": artists,
        "periods": periods,
        "baseline": periods[0] if periods else None,
        "years": sorted(data["ts"].dt.year.unique().tolist()),
    }

    safe_json = (
        json.dumps(payload, ensure_ascii=True, allow_nan=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )

    return """
<section class="chart">
    <h2>Discovery vs. Familiarity</h2>

    <p>
        New artists first appear in the complete uploaded history
        during that month.
    </p>

    <div class="discovery-controls">
        <label>
            Year
            <select id="discovery-year"></select>
        </label>

        <label>
            Month
            <select id="discovery-month"></select>
        </label>
    </div>

    <div id="discovery-chart"></div>

    <h3>Look up an artist</h3>

    <input
        id="discovery-search"
        type="search"
        placeholder="Start typing an artist name..."
        autocomplete="off"
        aria-label="Search an artist"
    >

    <div id="discovery-results"></div>

    <button id="discovery-clear" type="button">
        Clear selection
    </button>

    <p id="discovery-message" aria-live="polite">
        Search and select an artist to see their details.
    </p>

    <div id="discovery-details" hidden></div>

    <p class="discovery-note">
        The first observed month is excluded from the percentage
        chart because all artists appear for the first time there.
        Months without listening data appear as gaps.
    </p>
</section>

<style>
    .discovery-controls {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        margin: 20px 0;
    }

    .discovery-controls label {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .discovery-controls select,
    #discovery-search,
    #discovery-clear {
        padding: 10px 12px;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        background: white;
        color: #243247;
        font: inherit;
    }

    #discovery-search {
        width: 100%;
        box-sizing: border-box;
        margin-bottom: 10px;
    }

    #discovery-results {
        max-height: 200px;
        overflow-y: auto;
        margin-bottom: 12px;
    }

    #discovery-results button {
        display: block;
        width: 100%;
        padding: 10px 12px;
        text-align: left;
        background: white;
        border: 1px solid #eeeeee;
        font: inherit;
        cursor: pointer;
    }

    #discovery-results button:hover {
        background: #edf4ff;
    }

    #discovery-clear {
        cursor: pointer;
    }

    #discovery-details {
        padding: 18px;
        background: #f5f8fc;
        border-radius: 10px;
        line-height: 1.7;
    }

    .discovery-note {
        color: #64748b;
        font-size: 14px;
        line-height: 1.5;
    }
</style>

<script id="discovery-data" type="application/json">
__DISCOVERY_DATA__
</script>

<script>
(() => {
    const payload = JSON.parse(
        document.getElementById("discovery-data").textContent
    );

    const year = document.getElementById("discovery-year");
    const month = document.getElementById("discovery-month");
    const search = document.getElementById("discovery-search");
    const results = document.getElementById("discovery-results");
    const details = document.getElementById("discovery-details");
    const message = document.getElementById("discovery-message");

    let selectedArtist = null;

    const monthNames = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    ];

    year.add(new Option("All years", "all"));

    payload.years.forEach(value => {
        year.add(new Option(value, String(value)));
    });

    month.add(new Option("All months", "all"));

    monthNames.forEach((name, index) => {
        month.add(new Option(name, String(index + 1)));
    });

    function matches(period) {
        return (
            year.value === "all" ||
            Number(period.slice(0, 4)) === Number(year.value)
        ) && (
            month.value === "all" ||
            Number(period.slice(5, 7)) === Number(month.value)
        );
    }

    function updateDetails() {
        details.replaceChildren();
        details.hidden = selectedArtist === null;

        if (selectedArtist === null) {
            message.textContent =
                "Search and select an artist to see their details.";
            return;
        }

        const artist = payload.artists.find(
            item => item[0] === selectedArtist
        );

        const minutes = payload.records
            .filter(record =>
                record[1] === selectedArtist && matches(record[0])
            )
            .reduce((sum, record) => sum + record[2], 0);

        const firstInPeriod = matches(artist[1]);

        const observation = artist[1] === payload.baseline
            ? "Baseline observation: this artist already appears "
              + "in the first month of your history."
            : firstInPeriod
                ? "First recorded appearance falls within "
                  + "the selected period."
                : "First recorded appearance falls outside "
                  + "the selected period.";

        const lines = [
            ["Artist", artist[0]],
            ["First recorded play · Zurich time", artist[2]],
            [
                "Listening time in selected period",
                minutes.toFixed(1) + " minutes"
            ],
            ["Observation", observation]
        ];

        lines.forEach(([label, value]) => {
            const line = document.createElement("div");
            const heading = document.createElement("strong");

            heading.textContent = label + ": ";
            line.appendChild(heading);
            line.appendChild(document.createTextNode(value));
            details.appendChild(line);
        });

        message.textContent =
            "Artist details use the complete history. "
            + "Listening time follows your year and month filters.";
    }

    function updateChart() {
        const periods = payload.periods.filter(period =>
            period !== payload.baseline && matches(period)
        );

        const totals = new Map(
            periods.map(period => [period, [0, 0]])
        );

        payload.records.forEach(([period, artist, minutes, isNew]) => {
            if (totals.has(period)) {
                totals.get(period)[isNew ? 0 : 1] += minutes;
            }
        });

        const traces = [
            ["New artists", "#00B894"],
            ["Familiar artists", "#636EFA"]
        ].map(([name, color], index) => ({
            type: "bar",
            name: name,
            x: periods,
            y: periods.map(period => {
                const values = totals.get(period);
                const total = values[0] + values[1];

                return total > 0
                    ? values[index] / total * 100
                    : null;
            }),
            marker: {color: color},
            hovertemplate:
                "%{x}<br>Listening time share: %{y:.1f}%" +
                "<extra>%{fullData.name}</extra>"
        }));

        const hasData = traces[0].y.some(value => value !== null);

        if (typeof Plotly === "undefined") {
            document.getElementById("discovery-chart").textContent =
                "Plotly could not be loaded. Open the complete dashboard.";
            return;
        }

        Plotly.react(
            "discovery-chart",
            traces,
            {
                title: {text: "Discovery vs. Familiarity"},
                barmode: "stack",
                height: 450,
                paper_bgcolor: "white",
                plot_bgcolor: "white",
                font: {family: "Arial", color: "#333333"},
                margin: {l: 70, r: 30, t: 70, b: 100},
                xaxis: {
                    title: {text: "Month"},
                    showgrid: false
                },
                yaxis: {
                    title: {text: "Share of listening time (%)"},
                    range: [0, 100],
                    ticksuffix: "%",
                    gridcolor: "#EEEEEE"
                },
                legend: {orientation: "h", y: -0.25},
                annotations: hasData ? [] : [{
                    text: "No comparable listening data for this period.",
                    x: 0.5,
                    y: 0.5,
                    xref: "paper",
                    yref: "paper",
                    showarrow: false
                }]
            },
            {responsive: true, displaylogo: false}
        );
    }

    function updateSearch() {
        results.replaceChildren();

        const query = search.value.trim().toLowerCase();

        if (!query) return;

        const matches = payload.artists
            .map(item => item[0])
            .filter(name => name.toLowerCase().includes(query))
            .sort((a, b) => {
                const aStarts = a.toLowerCase().startsWith(query);
                const bStarts = b.toLowerCase().startsWith(query);

                if (aStarts !== bStarts) {
                    return aStarts ? -1 : 1;
                }

                return a.localeCompare(b);
            });

        if (!matches.length) {
            results.textContent = "No matching artists.";
            return;
        }

        matches.forEach(name => {
            const button = document.createElement("button");

            button.type = "button";
            button.textContent = name;

            button.addEventListener("click", () => {
                selectedArtist = name;
                search.value = "";
                results.replaceChildren();
                updateDetails();
            });

            results.appendChild(button);
        });
    }

    function updatePeriod() {
        updateDetails();
        updateChart();
    }

    year.addEventListener("change", updatePeriod);
    month.addEventListener("change", updatePeriod);
    search.addEventListener("input", updateSearch);

    document.getElementById("discovery-clear")
        .addEventListener("click", () => {
            selectedArtist = null;
            search.value = "";
            results.replaceChildren();
            updateDetails();
        });

    updatePeriod();
})();
</script>
    """.replace("__DISCOVERY_DATA__", safe_json)


# Native Python/Plotly API. The older HTML function above is kept only for
# preview_plots.py compatibility; Streamlit uses the functions below.
def discovery_data(df_plays):
    import pandas as pd
    from visualization.analysis_data import ARTIST, prepare_music
    data = prepare_music(df_plays, plays_only=True)
    data['month'] = data['ts'].dt.tz_localize(None).dt.to_period('M')
    first = data.groupby(ARTIST)['ts'].min()
    data['is_new'] = data['month'].eq(data[ARTIST].map(first.dt.tz_localize(None).dt.to_period('M')))
    baseline = data['month'].min() if not data.empty else None
    if data.empty:
        monthly = pd.DataFrame(columns=['New artists', 'Familiar artists', 'total_minutes'])
        monthly.index = pd.DatetimeIndex([], name='month')
    else:
        monthly = (data.groupby(['month', 'is_new'])['sec_played'].sum().div(60)
                   .unstack(fill_value=0).reindex(columns=[True, False], fill_value=0))
        monthly.columns = ['New artists', 'Familiar artists']
        monthly = monthly.reindex(pd.period_range(baseline, data['month'].max(), freq='M'), fill_value=0)
        monthly['total_minutes'] = monthly.sum(axis=1)
        monthly.index = monthly.index.to_timestamp()
        monthly.index.name = 'month'
    return data, monthly, first, baseline


def plot_discovery(df_plays, year=None, month=None):
    import plotly.graph_objects as go
    from visualization.analysis_data import empty_figure
    _, monthly, _, baseline = discovery_data(df_plays)
    if baseline is None:
        return empty_figure('Discovery vs. Familiarity', 'No listening data available.')
    display = monthly.loc[monthly.index != baseline.to_timestamp()]
    if year is not None:
        display = display.loc[display.index.year == int(year)]
    if month is not None:
        display = display.loc[display.index.month == int(month)]
    if display.empty or not display['total_minutes'].gt(0).any():
        return empty_figure('Discovery vs. Familiarity', 'No comparable listening data for this period.')
    fig = go.Figure()
    denominator = display['total_minutes'].where(display['total_minutes'].gt(0))
    for category, color in [('New artists', '#00B894'), ('Familiar artists', '#636EFA')]:
        fig.add_bar(name=category, x=display.index, y=display[category].div(denominator).mul(100),
                    marker_color=color, hovertemplate='%{x|%b %Y}<br>%{y:.1f}%<extra>%{fullData.name}</extra>')
    fig.update_layout(title='Discovery vs. Familiarity', template='plotly_white', barmode='stack', height=450,
                      legend=dict(orientation='h', y=-.25), paper_bgcolor='white', plot_bgcolor='white',
                      xaxis_title='Month', yaxis_title='Share of listening time (%)')
    fig.update_yaxes(range=[0,100], ticksuffix='%', gridcolor='#EEEEEE')
    fig.update_xaxes(showgrid=False, tickformat='%b %Y')
    return fig


def discovery_artist_details(df_plays, artist, year=None, month=None):
    from visualization.analysis_data import ARTIST, filter_period
    data, _, first, baseline = discovery_data(df_plays)
    if artist not in first.index:
        return None
    first_play = first.loc[artist]
    first_period = first_play.tz_localize(None).to_period('M')
    selected = filter_period(data, year, month)
    in_period = (year is None or first_play.year == int(year)) and (month is None or first_play.month == int(month))
    observation = ('Baseline observation' if first_period == baseline else
                   'First recorded appearance in selected period' if in_period else
                   'First recorded appearance outside selected period')
    return {'artist':artist, 'first_play':first_play,
            'minutes':float(selected.loc[selected[ARTIST].eq(artist), 'sec_played'].sum()/60),
            'observation':observation}
