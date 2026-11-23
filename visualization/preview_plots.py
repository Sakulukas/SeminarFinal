import json
import webbrowser
from pathlib import Path
import pandas as pd
import plotly.io as pio
from visualization.plot_top_artists import plot_top_artists
from visualization.plot_heatmap import plot_listening_heatmap
from visualization.plot_artist_history import plot_artist_history
from visualization.plot_skip_rates import render_skip_rates

def load_spotify_data(data_folder):
    files = sorted(
        data_folder.rglob("Streaming_History_Audio_*.json")
    )
    if not files:
        raise FileNotFoundError(
            "No Spotify audio files found in data_private."
        )
    rows = []
    for file in files:
        with file.open("r", encoding="utf-8") as f:
            records = json.load(f)
        for record in records:
            rows.append({
                "ts": record.get("ts"),
                "master_metadata_album_artist_name": record.get(
                    "master_metadata_album_artist_name"
                ),
                "sec_played": record.get("ms_played", 0) / 1000,
            })
    data = pd.DataFrame(rows)
    data["ts"] = pd.to_datetime(
        data["ts"], utc=True, errors="coerce"
    ).dt.tz_convert("Europe/Zurich")
    data = data.dropna(
        subset=["ts", "master_metadata_album_artist_name"]
    )
    return data.loc[data["sec_played"] > 0].copy()
if __name__ == "__main__":
    data_folder = Path(__file__).resolve().parent.parent / "data_private"
        # Keep short entries for skip analysis
    df_music = load_spotify_data(data_folder)

    # Existing charts still use plays of at least 30 seconds
    df_plays = df_music.loc[
        df_music["sec_played"] >= 30
    ].copy()
    artists = plot_top_artists(df_plays)
    heatmap = plot_listening_heatmap(df_plays)
    # Let both charts adapt to the page width
    for fig in (artists, heatmap):
        fig.update_layout(autosize=True, width=None)
    # Include Plotly once, directly in the HTML file
    artists_html = pio.to_html(
        artists,
        div_id="top-artists-chart",
        full_html=False,
        include_plotlyjs=True,
        config={"responsive": True, "displaylogo": False},
    )
    heatmap_html = pio.to_html(
        heatmap,
        div_id="listening-heatmap-chart",
        full_html=False,
        include_plotlyjs=False,
        config={"responsive": True, "displaylogo": False},
    )
        # Rank artists by total listening time
    artist_totals = (
        df_plays.groupby(
            "master_metadata_album_artist_name"
        )["sec_played"]
        .sum()
        .sort_values(ascending=False)
    )
    all_artists = artist_totals.index.tolist()
    initial_artists = all_artists[:5]
    # Prepare monthly values for every artist
    history_figure = plot_artist_history(
        df_plays, all_artists
    )
    history_payload = {
        "figure": json.loads(history_figure.to_json()),
        "artists": all_artists,
        "selected": initial_artists,
    }
    # Escape characters that could interfere with HTML
    history_json = (
        json.dumps(history_payload, ensure_ascii=True)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    history_section = """
    <section class="chart">
        <h2>Artist Listening History</h2>
        <p>Select up to 10 artists from your listening history.</p>
        <label for="artist-search">Search artists</label>
        <input
            id="artist-search"
            type="search"
            placeholder="Start typing an artist name..."
            autocomplete="off"
        >
        <div id="artist-results"></div>
        <div id="selected-artists"></div>
        <p id="artist-count" aria-live="polite"></p>
        <div id="artist-history-chart"></div>
    </section>
    <style>
        #artist-search {
            display: block;
            width: 100%;
            box-sizing: border-box;
            margin: 10px 0;
            padding: 12px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            font: inherit;
        }
        #artist-results {
            max-height: 220px;
            overflow-y: auto;
        }
        .artist-result {
            display: block;
            width: 100%;
            padding: 10px 12px;
            border: 0;
            border-bottom: 1px solid #eef2f6;
            background: white;
            text-align: left;
            font: inherit;
            cursor: pointer;
        }
        .artist-result:hover {
            background: #edf4ff;
        }
        #selected-artists {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 16px;
        }
        .artist-chip {
            padding: 8px 12px;
            border: 1px solid #c7d9ef;
            border-radius: 20px;
            background: #edf4ff;
            color: #243247;
            font: inherit;
            cursor: pointer;
        }
        #artist-count {
            color: #64748b;
            font-size: 13px;
        }
    </style>
    <script id="artist-history-data" type="application/json">
    __HISTORY_DATA__
    </script>
    <script>
    (() => {
        const payload = JSON.parse(
            document.getElementById(
                "artist-history-data"
            ).textContent
        );
        const search = document.getElementById("artist-search");
        const results = document.getElementById("artist-results");
        const chips = document.getElementById("selected-artists");
        const count = document.getElementById("artist-count");
        let selected = [...payload.selected];
        const traces = new Map(
            payload.figure.data.map(trace => [trace.name, trace])
        );
        const colors = [
            "#636EFA", "#EF553B", "#00CC96", "#AB63FA",
            "#FFA15A", "#19D3F3", "#FF6692", "#B6E880",
            "#FF97FF", "#FECB52"
        ];
        function updateChart() {
            const data = selected.map((artist, index) => {
                const trace = traces.get(artist);
                return {
                    ...trace,
                    line: {
                        ...trace.line,
                        color: colors[index]
                    }
                };
            });
            const layout = {
                ...payload.figure.layout,
                autosize: true
            };
            if (selected.length === 0) {
                layout.annotations = [{
                    text: "Select an artist to display their history.",
                    x: 0.5,
                    y: 0.5,
                    xref: "paper",
                    yref: "paper",
                    showarrow: false
                }];
            }
            Plotly.react(
                "artist-history-chart",
                data,
                layout,
                {responsive: true, displaylogo: false}
            );
        }
        function updateResults() {
            results.replaceChildren();
            const query = search.value.trim().toLowerCase();
            if (!query || selected.length >= 10) {
                return;
            }
            const matches = payload.artists
                .filter(artist =>
                    !selected.includes(artist) &&
                    artist.toLowerCase().includes(query)
                )
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
            if (matches.length === 0) {
                results.textContent = "No matching artists found.";
                return;
            }
            matches.forEach(artist => {
                const button = document.createElement("button");
                button.type = "button";
                button.className = "artist-result";
                button.textContent = artist;
                button.addEventListener("click", () => {
                    if (selected.length >= 10) return;
                    selected.push(artist);
                    search.value = "";
                    updateSelection();
                    search.focus();
                });
                results.appendChild(button);
            });
        }
        function updateSelection() {
            chips.replaceChildren();
            selected.forEach(artist => {
                const chip = document.createElement("button");
                chip.type = "button";
                chip.className = "artist-chip";
                chip.textContent = artist + " ×";
                chip.setAttribute("aria-label", "Remove " + artist);
                chip.addEventListener("click", () => {
                    selected = selected.filter(
                        name => name !== artist
                    );
                    updateSelection();
                });
                chips.appendChild(chip);
            });
            count.textContent =
                selected.length + " / 10 artists selected";
            search.disabled = selected.length >= 10;
            search.placeholder = search.disabled
                ? "Remove an artist to select another."
                : "Start typing an artist name...";
            updateResults();
            updateChart();
        }
        search.addEventListener("input", updateResults);
        updateSelection();
    })();
    </script>
    """.replace("__HISTORY_DATA__", history_json)
    # Embed aggregated listening totals only; original Spotify records stay local.
    filter_data = df_plays.copy()
    filter_data["year"] = filter_data["ts"].dt.year
    filter_data["month_number"] = filter_data["ts"].dt.month
    filter_data["weekday"] = filter_data["ts"].dt.dayofweek
    filter_data["hour"] = filter_data["ts"].dt.hour
    artist_rows = (
        filter_data.groupby(
            ["year", "month_number", "master_metadata_album_artist_name"]
        )["sec_played"].sum().div(60).reset_index()
    )
    heatmap_rows = (
        filter_data.groupby(
            ["year", "month_number", "weekday", "hour"]
        )["sec_played"].sum().div(60).reset_index()
    )
    filter_payload = {
        "years": sorted(filter_data["year"].unique().tolist()),
        "artists": artist_rows.values.tolist(),
        "heatmap": heatmap_rows.values.tolist(),
        "artistLayout": json.loads(artists.to_json())["layout"],
        "heatmapLayout": json.loads(heatmap.to_json())["layout"],
    }
    filter_json = (
        json.dumps(filter_payload, ensure_ascii=True, allow_nan=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    def period_controls(prefix):
        return (
            '<div class="period-controls">'
            f'<label>Year <select id="{prefix}-year"></select></label>'
            f'<label>Month <select id="{prefix}-month"></select></label>'
            '</div>'
        )

    page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>My Spotify Dashboard</title>
        <style>
            body {{
                margin: 0;
                padding: 32px 16px;
                background: #f5f7fa;
                color: #243247;
                font-family: Arial, sans-serif;
            }}
            main {{
                max-width: 1100px;
                margin: 0 auto;
            }}
            h1 {{
                margin-bottom: 8px;
            }}
            .intro {{
                margin-bottom: 28px;
                color: #64748b;
            }}
            .chart {{
                margin-bottom: 24px;
                padding: 16px;
                background: white;
                border-radius: 14px;
                box-shadow: 0 4px 18px rgba(0, 0, 0, 0.05);
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>
        <main>
            <h1>My Spotify Dashboard</h1>
            <p class="intro">
                Explore your favourite artists and listening habits.
            </p>
            <section class="chart">
                {period_controls("artists")}
                {artists_html}
            </section>
            <section class="chart">
                {period_controls("heatmap")}
                {heatmap_html}
            </section>
        </main>
    </body>
    </html>
    """
    page = page.replace(
        "</main>", history_section + "</main>"
    )
    filter_section = '\n<style>\n.period-controls {display:flex;flex-wrap:wrap;gap:20px;margin:8px 12px 16px}\n.period-controls label {display:flex;align-items:center;gap:10px;font-size:14px}\n.period-controls select {padding:9px 14px;border:1px solid #cbd5e1;border-radius:8px;background:white;color:#243247;font:inherit}\n</style>\n<script id="period-data" type="application/json">__PERIOD_DATA__</script>\n<script>\n(() => {\n    const payload = JSON.parse(document.getElementById("period-data").textContent);\n    const months = ["January","February","March","April","May","June",\n        "July","August","September","October","November","December"];\n    const days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];\n    const colors = ["#636EFA","#EF553B","#00CC96","#AB63FA","#FFA15A",\n        "#19D3F3","#FF6692","#B6E880","#FF97FF","#FECB52"];\n    const config = {responsive:true, displaylogo:false};\n    function controls(prefix, update) {\n        const year = document.getElementById(prefix + "-year");\n        const month = document.getElementById(prefix + "-month");\n        year.add(new Option("All years", "all"));\n        payload.years.forEach(value => year.add(new Option(value, String(value))));\n        month.add(new Option("All months", "all"));\n        months.forEach((name, index) => month.add(new Option(name, String(index+1))));\n        year.addEventListener("change", update);\n        month.addEventListener("change", update);\n    }\n    function matches(row, prefix) {\n        const year = document.getElementById(prefix + "-year").value;\n        const month = document.getElementById(prefix + "-month").value;\n        return (year === "all" || Number(year) === row[0]) &&\n            (month === "all" || Number(month) === row[1]);\n    }\n    function period(prefix) {\n        const year = document.getElementById(prefix + "-year");\n        const month = document.getElementById(prefix + "-month");\n        return month.options[month.selectedIndex].text + " · " +\n            year.options[year.selectedIndex].text;\n    }\n    function emptyNote(empty) {\n        return empty ? [{text:"No listening data for this period.",\n            x:0.5,y:0.5,xref:"paper",yref:"paper",showarrow:false}] : [];\n    }\n    function updateArtists() {\n        const totals = new Map();\n        payload.artists.filter(row => matches(row,"artists")).forEach(row => {\n            totals.set(row[2], (totals.get(row[2]) || 0) + row[3]);\n        });\n        const top = [...totals].sort((a,b) => b[1]-a[1] || a[0].localeCompare(b[0]))\n            .slice(0,10).reverse();\n        const layout = JSON.parse(JSON.stringify(payload.artistLayout));\n        delete layout.width;\n        layout.autosize = true;\n        layout.title = {text:"Your Top 10 Artists by Listening Time<br><sup>" + period("artists") + "</sup>"};\n        layout.annotations = emptyNote(top.length === 0);\n        layout.yaxis = {...layout.yaxis, categoryorder:"array", categoryarray:top.map(row=>row[0]), autorange:true};\n        layout.xaxis = {...layout.xaxis, autorange:true};\n        Plotly.react("top-artists-chart", [{type:"bar",orientation:"h",\n            x:top.map(row=>row[1]),y:top.map(row=>row[0]),\n            marker:{color:top.map((row,index)=>colors[index]),line:{width:0}},\n            hovertemplate:"%{y}<br>Listening time: %{x:.1f} minutes<extra></extra>"\n        }],layout,config);\n    }\n    function updateHeatmap() {\n        const rows = payload.heatmap.filter(row => matches(row,"heatmap"));\n        const values = Array.from({length:7},()=>Array(24).fill(0));\n        rows.forEach(row => {values[row[2]][row[3]] += row[4];});\n        const layout = JSON.parse(JSON.stringify(payload.heatmapLayout));\n        delete layout.width;\n        layout.autosize = true;\n        layout.title = {text:"Your Weekly Listening Pattern<br><sup>" + period("heatmap") + "</sup>",x:0.5};\n        layout.annotations = emptyNote(rows.length === 0);\n        layout.coloraxis.cmin = 0;\n        layout.coloraxis.cmax = Math.max(1,...values.flat());\n        layout.coloraxis.cauto = false;\n        Plotly.react("listening-heatmap-chart", [{type:"heatmap",\n            x:Array.from({length:24},(_,index)=>index),y:days,z:values,\n            coloraxis:"coloraxis",xgap:0,ygap:0,\n            hovertemplate:"%{y}, %{x}:00–%{x}:59<br>Listening time: %{z:.1f} minutes<extra></extra>"\n        }],layout,config);\n    }\n    controls("artists",updateArtists);\n    controls("heatmap",updateHeatmap);\n    updateArtists();\n    updateHeatmap();\n})();\n</script>\n'.replace("__PERIOD_DATA__", filter_json)
    page = page.replace("</body>", filter_section + "</body>")
    skip_section = render_skip_rates(df_music)

    page = page.replace(
        "</body>",
        skip_section + "</body>"
    )
    output_path = data_folder / "dashboard.html"
    output_path.write_text(page, encoding="utf-8")
    webbrowser.open(output_path.as_uri())
    print("Dashboard created successfully.")