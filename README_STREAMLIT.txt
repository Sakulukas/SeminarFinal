STREAMLIT / PLOTLY UPDATE
Based on Sakulukas/SeminarFinal main at 2a72ba92d4a1fb53e8d1515c764f47d8591bb6de.

INSTALL
1. Make a backup of your project or commit your intended code changes first.
2. Copy this archive's pages/ and visualization/ folders into the project root,
   keeping the folder structure. Replace the matching files. Keep all other files.
3. Install dependencies in the Python environment used for Streamlit:
   python -m pip install "streamlit>=1.49" "plotly>=5.18" "pandas>=2.0"
4. Start the existing site from the project root:
   python -m streamlit run Mainpage.py
5. Load data on the home page, then open Analysis.

OPTIONAL INDEPENDENT PREVIEW
   python -m streamlit run streamlit_demo.py
This provides an audio JSON upload and the same six charts. It does not require
config.py or the project's original cleaning module. It only extracts timestamp,
artist and duration for music entries. Raw IP fields are not included in charts.
When run locally, the upload goes to your local Python process. A hosted app
receives uploaded data on its host server.

INTEGRATION
The existing home page already sets session_state.plays and session_state.df.
The updated Analysis page calls:
   render_analysis(st.session_state.plays, st.session_state.get('df'),
                   style_figure=style_fig, card_factory=card)
All chart controls are native Streamlit widgets; all six figures use
st.plotly_chart. No iframe, components.html, or JavaScript is used in this path.
The existing site header/card styling remains integrated.

FILES
pages/Analysis.py                   Updated analysis page
visualization/analysis_data.py      Shared normalization, period filters, search
visualization/streamlit_dashboard.py Native controls and six-chart integration
visualization/plot_discovery.py     Adds Plotly API and artist detail calculation
visualization/plot_comebacks.py     Adds Plotly API, event table, last-play summary
visualization/plot_skip_rates.py    Adds Plotly API and adjustable skip calculation
streamlit_demo.py                   Optional standalone upload preview

The existing HTML render_* functions in the three plot modules are retained
for compatibility with your old preview_plots.py. Streamlit calls plot_* and
Python data functions instead. You do not need to edit preview_plots.py.

Keep the existing plot_top_artists.py, plot_heatmap.py and
plot_artist_history.py from the repository; this package imports them.

BEHAVIOR
- Top artists, heatmap, skips, discovery and comebacks have independent year/month filters.
- Existing three listening charts and discovery/comebacks use plays >=30 seconds.
- Skip chart uses ALL positive-duration music entries, with a configurable threshold
  and at least 20 entries per artist within the selected period. Exact threshold = play.
- Discovery first appearances and comeback pauses use the entire history BEFORE filtering.
- Discovery baseline month is omitted from percentages; inactive months are gaps.
- No long discovery/comeback detail lists until an artist is searched and selected.
- History supports up to 10 artists; exact substring search, starts-with first.
- Comeback threshold is configurable in days, using elapsed time between Spotify
  timestamps (which are recorded event times, not reconstructed playback starts).
- Last recorded play summary uses the full history, displays the dataset end and
  explicitly excludes unrecorded listening after the export.

VALIDATION
Checked synthetic data for boundary values, first appearances, zero/inactive months,
exact pauses, empty datasets and search ordering. Streamlit AppTest exercised the
actual Analysis page with six Plotly charts, filter/search reruns, skip threshold
changes and replacement datasets. No personal Spotify data was used.
Validated with pandas 2.2.3, Plotly 7.2.0, Streamlit 1.67.0.

GitHub has not been changed by this download. Copy/test locally, then commit only
these code files. Keep personal Spotify JSON and generated HTML out of Git.
