"""A module that contains classes that will help parse/process datasets"""

from csv import DictReader
from typing import Optional
from dataclasses import dataclass


@dataclass
class Song:
    """A data class that contains data of a song in our database

    Instance Attributes:
    - track_id: a unique identifier for the song
    - artists: a list of artists who made the song
    - album_name: the name of the album the song belongs to
    - track_name: the name of the song
    - popularity: score of the song's popularity
    - duration_ms: the length of the song in seconds
    - is_explicit: whether the song contains explicit content
    - energy: energy of the song
    - mode: modality (major or minor) of the song
    - acousticness: confidence of the song being acoustic
    - instrumentalness: confidence of the song being instrumental
    - valence: the positiveness of the song
    - tempo: tempo of the song in BPM
    - track_genre: the genre of the song
    """

    track_id: str
    artists: list[str]
    album_name: str
    track_name: str
    popularity: int
    duration_ms: int
    is_explicit: bool
    energy: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    valence: float
    tempo: float
    track_genre: str

    def __str__(self):
        """Return a string representation of the song"""
        return f"{self.track_name} by {', '.join(self.artists)}"


class Playlist:
    """This class has-a collection of song objects as well as  functions that help compute data of the playlist"""

    def __init__(self, name: str, songs: Optional[list[Song]] = None):
        """Initializes a playlist object with a name and an empty list of songs"""
        self.name: str = name
        self._songs: list[Song] = songs if songs is not None else []

    def __len__(self) -> int:
        """Return the number of songs in the playlist"""
        return len(self._songs)

    def add_song(self, song: Song) -> None:
        """Add a song to the playlist"""
        self._songs.append(song)

    def remove_song(self, song: Song) -> None:
        """Remove a song from the playlist"""
        self._songs.remove(song)

    def append_playlist(self, other: 'Playlist') -> None:
        """Append the songs from another playlist to this playlist"""
        self._songs.extend(other._songs)

    def convert_to_string(self) -> str:
        """
        Return a string representation of the playlist specifically intended to be copy-pasted into a spotify playlist.
        The format is 'spotify:track:{track_id}' for each song in the playlist.
        """
        res = []
        for song in self._songs:
            res.append(f'spotify:track:{song.track_id}')
        return '\n'.join(res)
    
    def taste_match(self, other: 'Playlist') -> float:
        """Return a percentage indicating how similar the taste in music is between two playlists"""
        if len(self._songs) == 0 or len(other._songs) == 0:
            return -1

        vector1 = self._vectorize_playlist()
        vector2 = other._vectorize_playlist()

        # Cosine similarity here returns a value > 0 since all features are positive
        cosine_similarity = self._cosine_similarity(vector1, vector2)
        return int(cosine_similarity * 100)

    def recommend_songs(self, song_manager: 'SongManager', limit: int) -> list[Song]:
        """Return a list of recommended songs based on the playlist"""
        if len(self._songs) == 0:
            return []

        playlist_vector = self._vectorize_playlist()
        recommended_songs = []

        for song in song_manager._songs.values():
            song_vector = self._vectorize_song(song)
            similarity = self._cosine_similarity(playlist_vector, song_vector)
            recommended_songs.append((song, similarity))
        
        # Sort by similarity first, then by popularity
        recommended_songs.sort(key=lambda x: (x[1], x[0].popularity), reverse=True)
        return [x[0] for x in recommended_songs[:limit]]

    def playlist_profile(self):
        """Return a dictionary with the 'profile' of the playlist, containing the top genre, average moods, etc."""
        top_genre = self._top_genre()
        avg_energy, _, _, avg_acousticness, avg_instrumentalness, avg_valence, _ = self._vectorize_playlist()

        res = {
            'top_genre': top_genre,
            'avg_energy': avg_energy,
            'avg_acousticness': avg_acousticness,
            'avg_instrumentalness': avg_instrumentalness,
            'avg_happiness': avg_valence
        }
        return res
    
    def _top_genre(self) -> str:
        """Return the top genre in the playlist"""
        genre_count = {}
        for song in self._songs:
            genre = song.track_genre
            if genre not in genre_count:
                genre_count[genre] = 0
            genre_count[genre] += 1
        
        top_genre = None
        max_count = 0
        for genre, count in genre_count.items():
            if count > max_count:
                top_genre = genre
                max_count = count
        
        return genre

    def _vectorize_song(self, song: Song) -> list[float]:
        """Return a list of the features of the song, normalized to a value roughly between 0 and 1"""
        return [song.energy, song.mode, song.speechiness, song.acousticness,
                song.instrumentalness, song.valence, song.tempo / 120
        ]

    def _vectorize_playlist(self) -> list[float]:
        """
        Return a list of the mean values of the features of the songs in the playlist
        Preconditions:
            - len(self._songs) > 0
        """
        num_features = 7
        playlist_vector = [0] * num_features

        for song in self._songs:
            song_vector = self._vectorize_song(song)
            for i in range(num_features):
                playlist_vector[i] += song_vector[i]
        
        return [x / len(self._songs) for x in playlist_vector]

    def _cosine_similarity(self, vector1: list[float], vector2: list[float]) -> float:
        """
        Return a value between -1 and 1 indicating the similarity between two vectors.
        Preconditions:
            - len(vector1) == len(vector2)
            - len(vector1) > 0
        """
        dot_product = sum(vector1[i] * vector2[i] for i in range(len(vector1)))
        norm1 = sum(x**2 for x in vector1) ** 0.5
        norm2 = sum(x**2 for x in vector2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0

        return dot_product / (norm1 * norm2)


class SongManager:
    """Class to load, parse, and manage the song data"""
   
    def __init__(self, file_path: Optional[str] = None):
        """"""
        self._song_data_raw: list[dict[str, str]] = []
        self._songs: dict[str, Song] = {}
        
        if file_path is not None:
            self.load_data_raw(file_path)
            self.parse_data()

    def load_data_raw(self, file_path: str):
        """Loads the raw song data from a CSV file into the _song_data_raw attribute"""
        with open(file_path, 'r', encoding="utf-8") as file:
            csv_reader = DictReader(file)
            for row in csv_reader:
                self._song_data_raw.append(row)

    def parse_data(self):
        """Parse the raw song data into Song objects and store them in the songs attribute"""
        for row in self._song_data_raw:
            track_id = row['track_id']
            artists = row['artists'].split(';')
            album_name = row['album_name']
            track_name = row['track_name']
            popularity = int(row['popularity'])
            duration_ms = int(row['duration_ms'])
            is_explicit = row['explicit'] == 'True'
            energy = float(row['energy'])
            mode = int(row['mode'])
            speechiness = float(row['speechiness'])
            acousticness = float(row['acousticness'])
            instrumentalness = float(row['instrumentalness'])
            valence = float(row['valence'])
            tempo = float(row['tempo'])
            track_genre = row['track_genre']

            song = Song(
                track_id=track_id,
                artists=artists,
                album_name=album_name,
                track_name=track_name,
                popularity=popularity,
                duration_ms=duration_ms,
                is_explicit=is_explicit,
                energy=energy,
                mode=mode,
                speechiness=speechiness,
                acousticness=acousticness,
                instrumentalness=instrumentalness,
                valence=valence,
                tempo=tempo,
                track_genre=track_genre
            )

            self._songs[track_id] = song

    def get_song_by_id(self, track_id: str) -> Optional[Song]:
        """Return a song object with the given track_id if it exists in the dataset"""
        if track_id not in self._songs:
            return None
        return self._songs[track_id]


# TEST STUFF
if __name__ == '__main__':
    sm = SongManager()
    sm.load_data_raw('dataset.csv')
    sm.parse_data()
    
    playlist1 = Playlist('playlist1')
    playlist1.add_song(sm.get_song_by_id('5SuOikwiRyPMVoIQDJUgSV'))
    playlist1.add_song(sm.get_song_by_id('4qPNDBW1i3p13qLCt0Ki3A'))
    playlist1.add_song(sm.get_song_by_id('4yzs6Ba0GQH55Zo66Q51PS'))
    # print(playlist1.recommend_songs(sm, 5))
    playlist2 = Playlist('playlist2')
