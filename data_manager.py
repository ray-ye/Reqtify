"""A module that contains classes that will help parse/process datasets"""

from math import log
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
    - track_genre: the genre of the song
    - duration_ms: the length of the song in seconds
    - popularity: score of the song's popularity
    - key: key of the song in pitch class notation
    - mode: modality (major or minor) of the song
    - tempo: tempo of the song in BPM
    - time_signature: time signature of the song from 3 to 7 representing (3/4 to 7/4)
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
    track_genre: str
    duration_ms: int
    popularity: int
    key: int
    mode: int
    tempo: float
    time_signature: int
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
        """Convert the playlist to a string specifically for intended to be copy pasted into a spotify playlist"""
        res = []
        for song in self._songs:
            res.append(f'spotify:track:{song.track_id}')
        return '\n'.join(res)

    def cosine_similarity(self, other: 'Playlist') -> float:
        """Return a value between -1 and 1 indicating the similarity between two playlists."""
        if len(self._songs) == 0 or len(other._songs) == 0:
            return -1

        mean_vector1 = [0] * 9
        mean_vector2 = [0] * 9

        for song in self._songs:

            mean_vector1[0] += song.is_explicit
            mean_vector1[1] += song.is_energetic
            mean_vector1[2] += song.is_instrumental
            mean_vector1[3] += song.is_acoustic
            mean_vector1[4] += song.is_happy
            mean_vector1[5] += song.mode

            mean_vector1[6] += song.tempo / 200
            mean_vector1[7] += song.time_signature / 7
            mean_vector1[8] += song.key / 11
        
        mean_vector1 = [x / len(self._songs) for x in mean_vector1]

        for song in other._songs:
            mean_vector2[0] += song.is_explicit
            mean_vector2[1] += song.is_energetic
            mean_vector2[2] += song.is_instrumental
            mean_vector2[3] += song.is_acoustic
            mean_vector2[4] += song.is_happy
            mean_vector2[5] += song.mode

            mean_vector2[6] += song.tempo / 200
            mean_vector2[7] += song.time_signature / 7
            mean_vector2[8] += song.key / 11
        
        mean_vector2 = [x / len(other._songs) for x in mean_vector2]

        # Cosine(theta) = (A . B) / (|A| * |B|)
        dot_product = sum(mean_vector1[i] * mean_vector2[i] for i in range(9))
        norm1 = sum(x**2 for x in mean_vector1) ** 0.5
        norm2 = sum(x**2 for x in mean_vector2) ** 0.5
        return dot_product / (norm1 * norm2)


class DataManager:
    """Class to load, parse, and manage the song data"""
    
    def __init__(self):
        """"""
        self._song_data_raw: list[dict[str, str]] = []
        self._songs: dict[str, Song] = {}

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
            track_genre = row['track_genre']
            duration_ms = int(row['duration_ms'])
            popularity = int(row['popularity'])
            key = int(row['key'])
            mode = int(row['mode'])
            tempo = float(row['tempo'])
            time_signature = int(row['time_signature'])

            is_explicit = True if row['explicit'] == 'True' else False
            # NOTE: some of these cutoff values may need to be adjusted
            is_energetic = float(row['energy']) > 0.5
            is_instrumental = float(row['instrumentalness']) > 0.5
            is_acoustic = float(row['acousticness']) > 0.5
            is_happy = float(row['valence']) > 0.5

            song = Song(track_id, artists, album_name, track_name, track_genre,
                        duration_ms, popularity, key, mode, tempo, time_signature,
                        is_explicit, is_energetic, is_instrumental, is_acoustic, is_happy)

            self._songs[track_id] = song

    def get_song_by_id(self, track_id: str) -> Optional[Song]:
        """Return a song object with the given track_id if it exists in the dataset"""
        if track_id not in self._songs:
            return None
        return self._songs[track_id]
    

data_manager = DataManager()
data_manager.load_data_raw('dataset.csv')
data_manager.parse_data()


# kpop
playlist1 = Playlist('playlist1')
playlist1.add_song(data_manager.get_song_by_id('3hkC9EHFZNQPXrtl8WPHnX'))
playlist1.add_song(data_manager.get_song_by_id('45OX2jjEw1l7lOFJfDP9fv'))
playlist1.add_song(data_manager.get_song_by_id('5aucVLKiumD89mxVCB4zvS'))
playlist1.add_song(data_manager.get_song_by_id('1R0hxCA5R7z5TiaXBZR7Mf'))

# kpop2
playlist2 = Playlist('playlist2')
playlist2.add_song(data_manager.get_song_by_id('4a9tbd947vo9K8Vti9JwcI'))
playlist2.add_song(data_manager.get_song_by_id('6cvGDClEIomp5CfKY3pQuZ'))
playlist2.add_song(data_manager.get_song_by_id('1KNi6PNEbQYnkxmqeschok'))

# eminem
playlist3 = Playlist('playlist3')
playlist3.add_song(data_manager.get_song_by_id('5W8HXMOMLtXLz0RGKUtnlZ'))
playlist3.add_song(data_manager.get_song_by_id('3r9m79pHykbs4FrCXlq1oO'))
playlist3.add_song(data_manager.get_song_by_id('1FJYqedfrSGitGHMvwRGBg'))

# juice wrld
playlist4 = Playlist('playlist4')
playlist4.add_song(data_manager.get_song_by_id('6XO8RlYuJCiI0v3IA48FeJ'))

print(playlist1.cosine_similarity(playlist2)) # 0.9625 kpop to kpop
print(playlist1.cosine_similarity(playlist3)) # 0.7294 kpop to eminem
print(playlist1.cosine_similarity(playlist4)) # 0.6992 kpop to juice wrld
print(playlist3.cosine_similarity(playlist4)) # 0.9835 eminem to juice wrld

print(playlist2.convert_to_string())

#['acoustic', 'afrobeat', 'alt-rock', 'alternative', 'ambient', 'anime', 'black-metal', 'bluegrass', 'blues', 'brazil', 'breakbeat', 'british', 'cantopop', 'chicago-house', 'children', 'chill', 'classical', 'club', 'comedy', 'country', 'dance', 'dancehall', 'death-metal', 'deep-house', 'detroit-techno', 'disco', 'disney', 'drum-and-bass', 'dub', 'dubstep', 'edm', 'electro', 'electronic', 'emo', 'folk', 'forro', 'french', 'funk', 'garage', 'german', 'gospel', 'goth', 'grindcore', 'groove', 'grunge', 'guitar', 'happy', 'hard-rock', 'hardcore', 'hardstyle', 'heavy-metal', 'hip-hop', 'honky-tonk', 'house', 'idm', 'indian', 'indie-pop', 'indie', 'industrial', 'iranian', 'j-dance', 'j-idol', 'j-pop', 'j-rock', 'jazz', 'k-pop', 'kids', 'latin', 'latino', 'malay', 'mandopop', 'metal', 'metalcore', 'minimal-techno', 'mpb', 'new-age', 'opera', 'pagode', 'party', 'piano', 'pop-film', 'pop', 'power-pop', 'progressive-house', 'psych-rock', 'punk-rock', 'punk', 'r-n-b', 'reggae', 'reggaeton', 'rock-n-roll', 'rock', 'rockabilly', 'romance', 'sad', 'salsa', 'samba', 'sertanejo', 'show-tunes', 'singer-songwriter', 'ska', 'sleep', 'songwriter', 'soul', 'spanish', 'study', 'swedish', 'synth-pop', 'tango', 'techno', 'trance', 'trip-hop', 'turkish', 'world-music']