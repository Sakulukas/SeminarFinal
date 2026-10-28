"""
Ideas Python Project:

1. Spotify ranking/new song manager
    - Be able to import albums from spotify, rank them on different aspects, compare with friends, etc.
    - Based on your rankings, get new recommendations
    - Own "spotify wrapped", as normal one is getting worse
    - Connect with RYM to recomment new stuff
    - how similar is your music to your friends'?
    More ideas
    - Listening clock: a heatmap of hour of day × day of week, and how it changed across years.
    - Skip analysis: which artists you skip most, and whether you skip more on shuffle. Skips are a nice honest signal of taste.
    - Taste eras: cluster months by their artist or genre mix to find “phases” and when they started and ended.
    - Obsessions: detect binges, like a song played 40 times in a week and then never again.
    - Loyalty vs. exploration: what share of each month’s listening was new artists, and which artists stayed with you for years.
    - Lifetime totals: total hours, top songs of all time, and a “your Wrapped for any date range” feature.
    - Context: listening by device and by country, which shows trips and travel.
    - Political compass type graph
    
    
    -- Actual Idea:
        - "How has my music taste changed over time?
            - Which types of music do I return to?
            - How long do trends last for me?
            - When do I listen?
            - How do I discover music?
            - What do I skip?
             ...
         
        ..How it would work:
          1. Data cleaning
              1.1. Merge JSON files
              1.2. Remove Podcasts (if desired) -- possible feature
              1.3. Remove 5-15sec. listens (skips)
              1.4. DOCUMENT PROCESS!!!!!
          2. Shape data
              2.1. Hours in week pivot table
              2.2. Monthly plays per artist/genre
              2.3. "Discovery Rate" of artists (how quickly do you discover artists / survival of artists in your listening behaviour)
              2.4. something something skip rate
          3. Visualization
              3.1. One chart per question + some stats below
          4. Bonus
              4.1. API pulls (classify own artists into genres, possible problem: Spotify genres are trash)
                  -- maybe try rym genres?
              4.2. Turn into app, s.t. anyone can load data (maybe good demonstration for December?)    
    
"""
