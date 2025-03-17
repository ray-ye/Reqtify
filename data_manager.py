"""A module that contains classes that will help parse/process datasets"""

from csv import DictReader
from typing import Optional
from dataclasses import dataclass


class DataManager:
    """"""
    
    def __init__(self):
        """"""
        self.song_data_raw: list[dict[str, str]] = []
        self.songs: list[Song] = []

    def load_data_raw(self, file_path: str):
        """Loads the raw song data from a CSV file into the song_data_raw attribute"""
        with open(file_path, 'r', encoding="utf-8") as file:
            csv_reader = DictReader(file)
            for row in csv_reader:
                self.song_data_raw.append(row)

    def parse_data(self):
        """Parse the raw song data into Song objects and store them in the songs attribute"""
        for row in self.song_data_raw:
            track_id = row['track_id']
            artists = row['artists'].split(';')
            album_name = row['album_name']
            track_name = row['track_name']
            duration_ms = int(row['duration_ms'])
            popularity = int(row['popularity'])

            is_explicit = True if row['explicit'] == True else False
            # NOTE: some of these cutoff values may need to be adjusted
            is_energetic = float(row['energy']) > 0.5
            is_instrumental = float(row['instrumentalness']) > 0.5
            is_acoustic = float(row['acousticness']) > 0.5
            is_happy = float(row['valence']) > 0.5

            song = Song(track_id, artists, album_name, track_name, duration_ms, popularity, is_explicit, is_energetic, is_instrumental, is_acoustic, is_happy)
            self.songs.append(song)

    def print_data(self):
        """TEMPORARY FUNCTION TO ANALYZE THE DATA - WILL BE REMOVED LATER"""
        import statistics

        energies = list(map(float, [row['energy'] for row in self.song_data_raw]))
        popularities = list(map(float,[row['popularity'] for row in self.song_data_raw]))
        keys = list(map(float,[row['key'] for row in self.song_data_raw]))
        modes = list(map(float,[row['mode'] for row in self.song_data_raw]))
        valences = list(map(float,[row['valence'] for row in self.song_data_raw]))
        speechiness = list(map(float,[row['speechiness'] for row in self.song_data_raw]))
        acousticness = list(map(float,[row['acousticness'] for row in self.song_data_raw]))
        instrumentalness = list(map(float,[row['instrumentalness'] for row in self.song_data_raw]))
        danceability = list(map(float,[row['danceability'] for row in self.song_data_raw]))

        print(statistics.correlation(energies, keys))
        print(statistics.correlation(energies, popularities))
        print(statistics.correlation(keys, popularities))
        print(statistics.correlation(energies, valences))
        print(statistics.correlation(modes, valences))
        print(statistics.correlation(speechiness, instrumentalness))
        print(statistics.correlation(danceability, energies))
    
        
@dataclass
class Song:
    """A data class that contains data of a song in our database

    Instance Attributes:
    - track_id: a unique identifier for the song
    - artists: a list of artists who made the song
    - album_name: the name of the album the song belongs to
    - track_name: the name of the song
    - duration_ms: the length of the song in seconds
    - popularity: score of the song's popularity
    - is_explicit: whether the song contains explicit content
    - is_energetic: whether the song is energetic
    - is_instrumental: whether the song is instrumental
    - is_acoustic: whether the song is acoustic
    - is_happy: whether the song is happy
    """

    track_id: str
    artists: list[str]
    album_name: str
    track_name: str
    duration_ms: int
    popularity: int
    is_explicit: bool
    is_energetic: bool
    is_instrumental: bool
    is_acoustic: bool
    is_happy: bool

    def __str__(self):
        """Return a string representation of the song"""
        return f"{self.track_name} by {', '.join(self.artists)}"


class Playlist:
    """This class has-a collection of song objects as well as functions that help compute data of the playlist"""
    
    def __init__(self, name: str, songs: Optional[list[Song]] = None):
        """Initializes a playlist object with a name and an empty list of songs"""
        self.name: str = name
        self.songs: list[Song] = songs if songs is not None else []
    
    def similarity(self, other: 'Playlist') -> float:
        """Return a value between -1 and 1 indicating the similarity between two playlists."""
        # NOTE: this algorithm may not be the best way to calculate similarity, but should be decent 

        if len(self.songs) == 0 or len(other.songs) == 0:
            return -1

        mean_vector1 = [0] * 5
        mean_vector2 = [0] * 5

        for song in self.songs:
            mean_vector1[0] += song.is_explicit
            mean_vector1[1] += song.is_energetic
            mean_vector1[2] += song.is_instrumental
            mean_vector1[3] += song.is_acoustic
            mean_vector1[4] += song.is_happy
        
        mean_vector1 = [x / len(self.songs) for x in mean_vector1]

        for song in other.songs:
            mean_vector2[0] += song.is_explicit
            mean_vector2[1] += song.is_energetic
            mean_vector2[2] += song.is_instrumental
            mean_vector2[3] += song.is_acoustic
            mean_vector2[4] += song.is_happy
        
        mean_vector2 = [x / len(other.songs) for x in mean_vector2]

        # Cosine(theta) = (A . B) / (|A| * |B|)
        dot_product = sum(mean_vector1[i] * mean_vector2[i] for i in range(5))
        norm1 = sum(x**2 for x in mean_vector1) ** 0.5
        norm2 = sum(x**2 for x in mean_vector2) ** 0.5
        return dot_product / (norm1 * norm2)




data_manager = DataManager()
data_manager.load_data_raw('dataset.csv')


playlist1 = Playlist('playlist1')
playlist2 = Playlist('playlist1')
print(playlist1.similarity(playlist2))
