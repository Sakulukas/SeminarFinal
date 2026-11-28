"""Native Streamlit widgets and Plotly charts. No HTML/JavaScript embedding."""
import calendar
from contextlib import nullcontext
import pandas as pd
import streamlit as st
from visualization.analysis_data import ARTIST, prepare_music, filter_period, search_artists
from visualization.plot_top_artists import plot_top_artists
from visualization.plot_heatmap import plot_listening_heatmap
from visualization.plot_artist_history import plot_artist_history
from visualization.plot_skip_rates import plot_skip_rates
from visualization.plot_discovery import plot_discovery, discovery_artist_details
from visualization.plot_comebacks import plot_comebacks, comeback_events, last_recorded_play


def period_controls(data, key):
    years = sorted(data['ts'].dt.year.unique().tolist())
    left, right = st.columns(2)
    year_key, month_key = key+'_year', key+'_month'
    # Drop old year selections when a new upload has a different date range.
    if st.session_state.get(year_key) not in [None, *years]:
        del st.session_state[year_key]
    year = left.selectbox('Year', [None, *years], format_func=lambda v:'All years' if v is None else str(v), key=year_key)
    month = right.selectbox('Month', [None, *range(1,13)],
        format_func=lambda v:'All months' if v is None else calendar.month_name[v], key=month_key)
    return year, month


def artist_lookup(data, key):
    query = st.text_input('Search an artist', key=key+'_query', placeholder='Start typing an artist name...')
    if not query.strip():
        st.caption('Enter a name to see matching artists. Starts-with matches appear first.')
        return None
    matches = search_artists(data[ARTIST].unique().tolist(), query)
    if not matches:
        st.info('No matching artists.')
        return None
    selection_key = key+'_artist'
    if st.session_state.get(selection_key) not in [None, *matches]:
        del st.session_state[selection_key]
    return st.selectbox('Select a matching artist', matches, index=None,
                        placeholder='Select an artist', key=selection_key)


def render_analysis(df_plays, df_music=None, style_figure=None, card_factory=None):
    """Call after set_page_config/render_header using cleaned session-state tables."""
    plays = prepare_music(df_plays, plays_only=True)
    music = prepare_music(df_music) if df_music is not None else None
    style = style_figure or (lambda fig:fig)
    card = card_factory or (lambda name:nullcontext())

    def show(fig, key):
        fig.update_layout(width=None, autosize=True)
        st.plotly_chart(style(fig), width="stretch", theme=None, key=key)

    with card('top_artists'):
        st.subheader('Top Artists')
        year, month = period_controls(plays,'top')
        data = filter_period(plays,year,month)
        if data.empty:
            st.info('No listening data for this period.')
        else:
            show(plot_top_artists(data),'top_chart')

    with card('heatmap'):
        st.subheader('Weekly Listening Pattern')
        year, month = period_controls(plays,'heat')
        data = filter_period(plays,year,month)
        if data.empty:
            st.info('No listening data for this period.')
        else:
            show(plot_listening_heatmap(data),'heat_chart')

    with card('artist_history'):
        st.subheader('Artist Listening History')
        ranking = plays.groupby(ARTIST)['sec_played'].sum().sort_values(ascending=False).index.tolist()
        query = st.text_input('Search artists to add', key='history_query', placeholder='Type part of an artist name...')
        current = st.session_state.get('history_artists',ranking[:5])
        current = [a for a in current if a in ranking]
        if 'history_artists' in st.session_state and current != st.session_state['history_artists']:
            st.session_state['history_artists'] = current
        matches = search_artists(ranking,query) if query.strip() else []
        options = list(dict.fromkeys(current+matches))
        chosen = st.multiselect('Pick up to 10 artists',options,default=current,max_selections=10,key='history_artists')
        st.caption('Search uses consecutive letters, ignoring case. Clear a selection to remove an artist.')
        if chosen:
            show(plot_artist_history(plays,chosen),'history_chart')
        else:
            st.info('Search and select at least one artist.')

    with card('skip_rates'):
        st.subheader('Skip Rates by Artist')
        if music is None:
            st.info('Skip analysis needs the complete cleaned music table, including entries shorter than 30 seconds.')
        else:
            year, month = period_controls(music,'skip')
            threshold = st.number_input('Skip threshold (seconds)',min_value=1,value=30,step=1,key='skip_seconds')
            st.caption('Skip = more than 0 seconds and less than the threshold. Artists need at least 20 entries in the selected period.')
            show(plot_skip_rates(music,threshold,year,month),'skip_chart')

    with card('discovery'):
        st.subheader('Discovery vs. Familiarity')
        year, month = period_controls(plays,'discovery')
        show(plot_discovery(plays,year,month),'discovery_chart')
        st.caption('New means first recorded in the complete uploaded history. The first observed month is baseline and excluded from the chart. Months without plays remain gaps.')
        artist = artist_lookup(plays,'discovery_lookup')
        if artist is not None:
            details = discovery_artist_details(plays,artist,year,month)
            st.write('Artist:',artist)
            st.write('First recorded play:',details['first_play'].strftime('%d %b %Y, %H:%M %Z'))
            st.metric('Listening time in selected period',f"{details['minutes']:.1f} minutes")
            st.caption(details['observation'])

    with card('comebacks'):
        st.subheader('Artist Comebacks')
        year, month = period_controls(plays,'comeback')
        days = st.number_input('Minimum pause (days)',min_value=1,value=180,step=1,key='comeback_days')
        st.caption('Filters apply to the return date. Pauses use the exact elapsed time between consecutive recorded plays, calculated before filtering.')
        artist = artist_lookup(plays,'comeback_lookup')
        show(plot_comebacks(plays,days,year,month,artist),'comeback_chart')
        if artist is not None:
            events = comeback_events(plays,days,year,month,artist)
            st.write(f'{len(events)} matching comebacks for {artist}.')
            if not events.empty:
                table = events.rename(columns={ARTIST:'Artist','previous_play':'Previous recorded play','ts':'Return play','pause_days':'Pause (days)'}).copy()
                for col in ['Previous recorded play','Return play']:
                    table[col] = table[col].dt.strftime('%d %b %Y, %H:%M %Z')
                table['Pause (days)'] = table['Pause (days)'].round(2)
                st.dataframe(table,hide_index=True,width="stretch")
            last = last_recorded_play(plays,artist)
            st.write('Last recorded play:',last['last_play'].strftime('%d %b %Y, %H:%M %Z'))
            st.metric('Days since last recorded play',f"{last['days_since']:.1f}")
            st.caption('Dataset ends: '+last['dataset_end'].strftime('%d %b %Y, %H:%M %Z')+'. This summary uses the complete history. Listening after the export is not included.')
        else:
            st.caption('Search and select an artist to see their detailed comeback history and last recorded play.')
        st.caption('The chart shows up to 15 artists. Missing export data can look like a listening pause.')
