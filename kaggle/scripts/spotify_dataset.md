
## About Dataset

This dataset contains information about Spotify tracks across 125 different music genres, where each row represents a single song and each column represents a specific attribute related to that track. Along with basic metadata such as track name, artist, and genre label, the dataset includes several numerical audio features extracted by Spotify’s audio analysis system, such as danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, valence, tempo, and duration. These features quantitatively describe the musical characteristics and mood of each track, making the dataset highly suitable for data analysis, visualization, and machine learning tasks like genre classification, clustering, recommendation systems, and mood prediction. Since the data is provided in CSV (Comma-Separated Values) format, it is tabular, lightweight, and easy to load into tools like Python (Pandas), R, Excel, or SQL databases for quick processing and modeling.
Spotify Tracks Dataset
Usage

You can use this dataset for:
    Building a music **recommendation system** based on user preferences.
    **Classifying songs into genres** using their audio features.
    **Performing music data analysis** or any other related project.

### Column Description

- track_id – A unique ID given to each song by Spotify.

- artists – Name of the artist(s) who performed the song. Multiple artists are separated by a semicolon (;).

- album_name – The name of the album where the song appears.

- track_name – The name of the song.

- popularity – A value between 0 and 100 that shows how popular the song is. Higher value means more popular. It is based mainly on play count and how recent those plays are.

- duration_ms – The length of the song in milliseconds.

-   explicit – Indicates whether the song has explicit (adult) lyrics.
    - true = Yes
    - false = No or unknown 

- danceability – How suitable the song is for dancing (0 = least danceable, 1 = most danceable).

- energy – How energetic the song feels (0 = calm/soft, 1 = very energetic/loud).

- key – The musical key of the song (e.g., C, D, E). If unknown, the value is -1.

- loudness – The overall loudness of the song in decibels (dB).

- mode – Indicates whether the song is:
    - 1 = Major (usually sounds happy)
    - 0 = Minor (usually sounds sad) 

- speechiness – Measures how much spoken content is in the song.
    - Close to 1 = Mostly spoken words (e.g., podcast)
    - Between 0.33–0.66 = Mix of speech and music (e.g., rap)
    - Below 0.33 = Mostly music 

- acousticness – Likelihood that the song is acoustic (1 = very likely acoustic).

- instrumentalness – Likelihood that the song has no vocals (1 = no singing).

- liveness – Probability that the song was recorded live (higher value = more likely live).

- valence – Describes the mood of the song.
    - High value = Happy/positive
    - Low value = Sad/negative 

- tempo – The speed of the song measured in beats per minute (BPM).

- time_signature – Number of beats in each bar (usually between 3 and 7).

- track_genre – The genre category of the song.
