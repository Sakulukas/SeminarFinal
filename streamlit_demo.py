"""Optional independent local preview: python -m streamlit run streamlit_demo.py"""
import json
import pandas as pd
import streamlit as st
from visualization.streamlit_dashboard import render_analysis

st.set_page_config(page_title='Spotify Listening Analysis',layout='wide')
st.title('Spotify Listening Analysis')
st.caption('Local preview. Start Streamlit on your own computer to keep uploads on that computer.')
files = st.file_uploader('Upload Spotify Extended Streaming History audio JSON files',type='json',accept_multiple_files=True)
if not files:
    st.info('Select your audio history files to display the six charts.')
    st.stop()
rows=[]
try:
    for file in files:
        records=json.load(file)
        if not isinstance(records,list):
            raise ValueError(f'{file.name}: expected a list of Spotify history entries.')
        for record in records:
            if not isinstance(record,dict):
                raise ValueError(f'{file.name}: invalid history entry.')
            if not record.get('master_metadata_track_name'):
                continue
            if record.get('audiobook_title') or record.get('audiobook_uri'):
                continue
            seconds=pd.to_numeric(record.get('ms_played'),errors='coerce')
            rows.append({'ts':record.get('ts'),
                         'master_metadata_album_artist_name':record.get('master_metadata_album_artist_name'),
                         'sec_played':seconds/1000})
except (ValueError,TypeError) as error:
    st.error(str(error))
    st.stop()
music=pd.DataFrame(rows,columns=['ts','master_metadata_album_artist_name','sec_played'])
render_analysis(music,music)
