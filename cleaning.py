"""
DATA CLEANING TO-DO LIST:
0. load data in, concatenate, etc.
1. get rid of IP-Address
2. change time from UTC to CET
3. (maybe) get rid of device used to play song
4. leave in conn_country
5. ms_played at least 30 seconds
6. chang ms_played to sec_played
7. delete all things regarding podcasts and audiobooks
8. remove incognito mode(who uses this?)


Individual topics:

0.1 -- Lukas' dataset: 
    for some years, there are 2 files, e.g. Streaming_History_Audio_2022 and Streaming_History_Audio_2022_1
    -> Hypothesis: Spotify splits data sets once they reach roughly 12.4MB. 12.4, since this is the threshhold in three seperate years. (not exact)
                   Checking the dates: the last play of 'Streaming_History_Audio_2023' is at 2023-11-23T17:00:43Z, the first play of Streaming_History_Audio_2023_1 is at 2023-11-23T17:00:44Z.
                    So include both.


"""