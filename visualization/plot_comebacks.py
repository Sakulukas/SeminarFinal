import json
import pandas as pd


ARTIST = "master_metadata_album_artist_name"


def render_comebacks(df_plays):
    data = df_plays.copy()

    data["ts"] = pd.to_datetime(
        data["ts"], utc=True
    ).dt.tz_convert("Europe/Zurich")

    data = (
        data.dropna(subset=["ts", ARTIST])
        .sort_values("ts")
    )

    # Calculate gaps using the complete history
    data["previous"] = data.groupby(ARTIST)["ts"].shift()

    events = []

    for _, row in data.dropna(subset=["previous"]).iterrows():
        days = (
            row["ts"] - row["previous"]
        ).total_seconds() / 86400

        if days >= 1:
            events.append([
                row[ARTIST],
                row["previous"].isoformat(),
                row["ts"].isoformat(),
                days,
                row["ts"].strftime("%Y-%m"),
            ])

    last_plays = data.groupby(ARTIST)["ts"].max()

    artists = [
        [artist, timestamp.isoformat()]
        for artist, timestamp in last_plays.items()
    ]

    payload = {
        "events": events,
        "artists": artists,
        "years": sorted(data["ts"].dt.year.unique().tolist()),
        "end": (
            data["ts"].max().isoformat()
            if not data.empty else None
        ),
    }

    safe_json = (
        json.dumps(payload, ensure_ascii=True, allow_nan=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )

    return """
    <section class="chart">
        <h2>Artist Comebacks</h2>

        <p>
            Choose a minimum pause and a return period.
            Pauses are calculated between consecutive recorded
            plays of the same artist.
        </p>

        <div class="comeback-controls">
            <label>
                Return year
                <select id="comeback-year"></select>
            </label>

            <label>
                Return month
                <select id="comeback-month"></select>
            </label>

            <label>
                Minimum pause (days)
                <input
                    id="comeback-days"
                    type="number"
                    min="1"
                    step="1"
                    value="180"
                >
            </label>
        </div>

        <label for="comeback-search">Search an artist</label>

        <input
            id="comeback-search"
            type="search"
            placeholder="Start typing an artist name..."
            autocomplete="off"
        >

        <div id="comeback-results"></div>

        <p id="comeback-selected"></p>

        <button id="comeback-clear" type="button">
            Show all artists
        </button>

        <p id="comeback-message" aria-live="polite"></p>

        <div id="comeback-chart"></div>

        <div
            id="comeback-details"
            class="comeback-table-container"
            hidden
        >
            <table class="comeback-table">
                <thead>
                    <tr>
                        <th>Artist</th>
                        <th>Previous play · Zurich time</th>
                        <th>Return play · Zurich time</th>
                        <th>Pause</th>
                    </tr>
                </thead>
                <tbody id="comeback-table-body"></tbody>
            </table>
        </div>

        <h3>Last recorded play</h3>
        <p id="comeback-last-play"></p>

        <p>
            Up to 15 artists appear in the chart.
            All matching comebacks appear in the table.
            Missing export data can look like a listening pause.
        </p>
    </section>

    <style>
        .comeback-controls {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin: 20px 0;
        }

        .comeback-controls label {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .comeback-controls select,
        .comeback-controls input,
        #comeback-search {
            padding: 10px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            background: white;
            font: inherit;
        }

        #comeback-days {
            width: 140px;
        }

        #comeback-search {
            display: block;
            width: 100%;
            box-sizing: border-box;
            margin: 10px 0;
        }

        #comeback-results {
            max-height: 200px;
            overflow-y: auto;
        }

        #comeback-results button {
            display: block;
            width: 100%;
            padding: 10px;
            background: white;
            border: 1px solid #eeeeee;
            text-align: left;
            font: inherit;
            cursor: pointer;
        }

        #comeback-results button:hover {
            background: #edf4ff;
        }

        #comeback-clear {
            padding: 8px 12px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            background: white;
            cursor: pointer;
        }

        .comeback-table-container {
            max-height: 350px;
            overflow: auto;
        }

        .comeback-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }

        .comeback-table th,
        .comeback-table td {
            padding: 10px;
            border-bottom: 1px solid #eeeeee;
            text-align: left;
        }
    </style>

    <script id="comeback-data" type="application/json">
        __COMEBACK_DATA__
    </script>

    <script>
    (() => {
        const payload = JSON.parse(
            document.getElementById("comeback-data").textContent
        );

        const year = document.getElementById("comeback-year");
        const month = document.getElementById("comeback-month");
        const daysInput = document.getElementById("comeback-days");
        const search = document.getElementById("comeback-search");
        const results = document.getElementById("comeback-results");
        const selectedLabel = document.getElementById("comeback-selected");
        const message = document.getElementById("comeback-message");
        const body = document.getElementById("comeback-table-body");
        const lastPlay = document.getElementById("comeback-last-play");

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

        function formatDate(value) {
            return new Date(value).toLocaleString("en-GB", {
                timeZone: "Europe/Zurich",
                year: "numeric",
                month: "short",
                day: "2-digit",
                hour: "2-digit",
                minute: "2-digit"
            });
        }

        function matches(period) {
            return (
                year.value === "all" ||
                Number(period.slice(0, 4)) === Number(year.value)
            ) && (
                month.value === "all" ||
                Number(period.slice(5, 7)) === Number(month.value)
            );
        }

        function updateLastPlay() {
            const exportEnd = payload.end
                ? formatDate(payload.end)
                : "No recorded plays";

            if (!selectedArtist) {
                lastPlay.textContent =
                    "Select an artist to see their last recorded play. " +
                    "Dataset ends: " + exportEnd + ".";
                return;
            }

            const artist = payload.artists.find(
                item => item[0] === selectedArtist
            );

            const daysSince = Math.max(
                0,
                (Date.now() - Date.parse(artist[1])) / 86400000
            );

            lastPlay.textContent =
                selectedArtist + ": " + formatDate(artist[1]) +
                ". " + daysSince.toFixed(1) +
                " days since the last recorded play, as of today. " +
                "Dataset ends: " + exportEnd + ". " +
                "Listening after the export is not included. " +
                "This summary uses the complete history.";
        }

        function update() {
            const minimumDays = Number(daysInput.value);

            if (
                daysInput.value.trim() === "" ||
                !Number.isInteger(minimumDays) ||
                minimumDays < 1
            ) {
                message.textContent =
                    "Enter a whole number of at least 1 day.";
                return;
            }

            const events = payload.events
                .filter(event =>
                    event[3] >= minimumDays &&
                    matches(event[4]) &&
                    (
                        selectedArtist === null ||
                        event[0] === selectedArtist
                    )
                )
                .sort((a, b) => b[2].localeCompare(a[2]));

            // Show up to 15 artists, ranked by comeback count
            const counts = new Map();

            events.forEach(event => {
                counts.set(
                    event[0],
                    (counts.get(event[0]) || 0) + 1
                );
            });

            const topArtists = [...counts]
                .sort((a, b) =>
                    b[1] - a[1] || a[0].localeCompare(b[0])
                )
                .slice(0, 15)
                .map(item => item[0]);

            const chartEvents = events.filter(
                event => topArtists.includes(event[0])
            );

            Plotly.react(
                "comeback-chart",
                [{
                    type: "scatter",
                    mode: "markers",
                    x: chartEvents.map(event => event[2]),
                    y: chartEvents.map(event => event[0]),
                    customdata: chartEvents.map(event => [
                        formatDate(event[1]),
                        formatDate(event[2]),
                        event[3]
                    ]),
                    marker: {
                        size: 12,
                        color: chartEvents.map(event => event[3]),
                        colorscale: "Teal",
                        showscale: chartEvents.length > 0,
                        colorbar: {
                            title: {text: "Days away"}
                        }
                    },
                    hovertemplate:
                        "%{y}<br>" +
                        "Previous play: %{customdata[0]}<br>" +
                        "Return play: %{customdata[1]}<br>" +
                        "Pause: %{customdata[2]:.2f} days" +
                        "<extra></extra>"
                }],
                {
                    title: {text: "Artist Comebacks"},
                    height: 560,
                    paper_bgcolor: "white",
                    plot_bgcolor: "white",
                    font: {family: "Arial", color: "#333333"},
                    margin: {l: 140, r: 80, t: 70, b: 60},
                    xaxis: {
                        title: {text: "Return date"},
                        showgrid: false
                    },
                    yaxis: {
                        automargin: true,
                        gridcolor: "#EEEEEE"
                    },
                    annotations: events.length ? [] : [{
                        text: "No matching comebacks.",
                        x: 0.5,
                        y: 0.5,
                        xref: "paper",
                        yref: "paper",
                        showarrow: false
                    }]
                },
                {responsive: true, displaylogo: false}
            );

            body.replaceChildren();
            const hasSelection = selectedArtist !== null;

            document.getElementById(
                "comeback-details"
            ).hidden = !hasSelection;            

            const detailEvents = hasSelection ? events : [];

            detailEvents.forEach(event => {            
                const row = document.createElement("tr");

                [
                    event[0],
                    formatDate(event[1]),
                    formatDate(event[2]),
                    event[3].toFixed(2) + " days"
                ].forEach(value => {
                    const cell = document.createElement("td");
                    cell.textContent = value;
                    row.appendChild(cell);
                });

                body.appendChild(row);
            });

            
            message.textContent = hasSelection
                ? events.length + " matching comebacks for "
                    + selectedArtist + "."
                : "Search and select an artist to see their comeback details.";
                
            updateLastPlay();
        }

        function updateSearch() {
            results.replaceChildren();

            const query = search.value.trim().toLowerCase();

            if (!query) return;

            const matches = payload.artists
                .map(item => item[0])
                .filter(name => name.toLowerCase().includes(query))
                .sort((a, b) => {
                    const aStarts =
                        a.toLowerCase().startsWith(query);

                    const bStarts =
                        b.toLowerCase().startsWith(query);

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
                    selectedLabel.textContent =
                        "Selected artist: " + name;

                    search.value = "";
                    results.replaceChildren();

                    update();
                });

                results.appendChild(button);
            });
        }

        document.getElementById("comeback-clear")
            .addEventListener("click", () => {
                selectedArtist = null;
                selectedLabel.textContent = "";
                search.value = "";
                results.replaceChildren();
                update();
            });

        year.addEventListener("change", update);
        month.addEventListener("change", update);
        daysInput.addEventListener("input", update);
        search.addEventListener("input", updateSearch);

        update();
    })();
    </script>
    """.replace("__COMEBACK_DATA__", safe_json)