"""A module that contains classes that will help parse/process datasets"""

from csv import DictReader
from typing import Optional, Any
from dataclasses import dataclass
import json
import pygame
import pyperclip
from button import Button


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

    def __str__(self) -> str:
        """Return a string representation of the song"""
        return f"{self.track_name} by {', '.join(self.artists)}"


class Playlist:
    """This class has-a collection of song objects as well as functions that help compute data of the playlist

    Instance Attributes:
    - name: name of playlist
    - _songs: a list of songs
    - _display: displays songs

    """
    name: str
    _songs: dict
    _displays: dict

    def __init__(self, name: str, songs: Optional[dict] = None) -> None:
        """Initializes a playlist object with a name and an empty list of songs"""
        self.name = name
        self._songs = songs if songs is not None else {}  # I changed this to a dict mapping id to song object - R

        self._displays = {}

    def __len__(self) -> int:
        """Return the number of songs in the playlist"""
        return len(self._songs)

    def add_song(self, song: Song) -> None:
        """Add a song to the playlist"""
        self._songs[song.track_id] = song

    def remove_song(self, song: Song) -> None:
        """Remove a song from the playlist"""
        del self._songs[song.track_id]

    def append_playlist(self, other: 'Playlist') -> None:
        """Append the songs from another playlist to this playlist"""
        for song in other.get_songs().values():
            self._songs[song.track_id] = song

    def get_songs(self) -> dict:
        """Return the list of songs in the playlist"""
        return self._songs

    def convert_to_string(self) -> str:
        """
        Return a string representation of the playlist specifically intended to be copy-pasted into a spotify playlist.
        The format is 'spotify:track:{track_id}' for each song in the playlist.
        """
        res = []
        for song_id in self._songs:
            res.append(f'spotify:track:{song_id}')
        return '\n'.join(res)

    def copy_to_clipboard(self) -> None:
        """Copy the playlist to the clipboard"""
        pyperclip.copy(self.convert_to_string())
        pyperclip.paste()

    def taste_match(self, other: 'Playlist') -> float:
        """Return a percentage indicating how similar the taste in music is between two playlists"""
        if len(self._songs) == 0 or len(other._songs) == 0:
            return 0

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

    def playlist_profile(self) -> dict:
        """
        Return a dictionary with the 'profile' of the playlist, containing the top genre, average moods, etc.
        (in percentage).
        """
        if len(self._songs) == 0:
            return {
                'Top genre': '[Empty]',
                'Avg energy': 0,
                'Avg acousticness': 0,
                'Avg instrumentalness': 0,
                'Avg happiness': 0
            }
        top_genre = self._top_genre()
        avg_energy, _, _, avg_acousticness, avg_instrumentalness, avg_valence, _ = self._vectorize_playlist()

        res = {
            'Top genre': top_genre,
            'Avg energy': round(avg_energy * 100, 2),
            'Avg acousticness': round(avg_acousticness * 100, 2),
            'Avg instrumentalness': round(avg_instrumentalness * 100, 2),
            'Avg happiness': round(avg_valence * 100, 2)
        }
        return res

    def _top_genre(self) -> str:
        """Return the top genre in the playlist"""
        genre_count = {}

        if not self._songs:
            return "[Empty]"

        for song in self._songs.values():
            genre = song.track_genre
            if genre not in genre_count:
                genre_count[genre] = 0
            genre_count[genre] += 1

        max_count = 0
        for genre, count in genre_count.items():
            if count > max_count:
                max_count = count

        return genre

    def _vectorize_song(self, song: Song) -> list[float]:
        """Return a list of the features of the song, normalized to a value roughly between 0 and 1"""
        return [song.energy, song.mode, song.speechiness, song.acousticness,
                song.instrumentalness, song.valence, song.tempo / 120]

    def _vectorize_playlist(self) -> list[float]:
        """
        Return a list of the mean values of the features of the songs in the playlist
        Preconditions:
            - len(self._songs) > 0
        """
        num_features = 7
        playlist_vector = [0] * num_features

        for song in self._songs.values():
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

    def load_displays(self, screen: Any, start_height: int, songs: list[Song], profile: Optional[bool] = None) -> None:
        """Loads the displays"""
        self._displays = {}
        margin = 15
        button_margin = 25
        pos = (margin, start_height)
        max_height = screen.get_height() - 100
        rect_dimensions = (screen.get_width() / 2 - margin * 1.5, 65)
        save_button_size = rect_dimensions[1] - 40

        for i in range(len(songs)):
            if i == 0:
                pos = (margin, pos[1])

            elif profile:
                pos = (margin, pos[1] + rect_dimensions[1] + margin)
                if pos[1] + rect_dimensions[1] + margin > max_height:
                    return

            elif (i + 1) % 2 == 0 and not pos[1] + rect_dimensions[1] + margin > max_height:
                pos = (margin * 2 + rect_dimensions[0], pos[1])

            else:
                pos = (margin, pos[1] + rect_dimensions[1] + margin)
                if pos[1] + rect_dimensions[1] + margin > max_height:
                    return

            save_button = Button("assets/unheart.png",
                                 (pos[0] + rect_dimensions[0] - save_button_size / 2 - button_margin,
                                  pos[1] + rect_dimensions[1] / 2 + 3),
                                 (save_button_size, save_button_size))

            self._displays[songs[i].track_id] = Display(pos, rect_dimensions, songs[i], save_button)

    def update_display(self, user: Any) -> None:
        """Updates the displays"""
        for display in self._displays:
            if display in user.playlist.get_songs():
                self._displays[display].button.image = pygame.image.load("assets/heart.png").convert_alpha()
                self._displays[display].button.update_image()
            else:
                self._displays[display].button.image = pygame.image.load("assets/unheart.png").convert_alpha()
                self._displays[display].button.update_image()

    def draw(self, screen: Any) -> None:
        """Draws the displays"""
        for display in self._displays.values():
            display.draw(screen)

    def get_displays(self) -> dict:
        """Returns displays"""
        return self._displays


class Display():
    """A data class that displays anything necessary 

    Instance Attributes:
    - pos: position of  display
    - dimension: dimension of display
    - song: the songs being displayed
    - button: buttons used in display
    """
    pos: tuple
    dimension: tuple
    song: Song
    button: Any

    def __init__(self, pos: tuple, dimension: tuple, song: Song, save_button: Any) -> None:
        self.pos = pos
        self.dimension = dimension
        self.song = song
        self.button = save_button

    def draw(self, screen: Any) -> None:
        """Draws onto the menu"""
        margin = 25
        font_size1 = 20
        font_size2 = 12
        font1 = pygame.font.SysFont("Arial", font_size1)
        font2 = pygame.font.SysFont("Arial", font_size2)
        rect = pygame.Rect(self.pos, self.dimension)

        save_button_size = self.dimension[1] - 40
        album_cover_size = self.dimension[1] - 10

        if len(self.song.artists) > 2:
            artists = ', '.join(self.song.artists[:2]) + ",..."
        else:
            artists = ', '.join(self.song.artists)

        if len(self.song.track_name) > 50:
            song_name = self.song.track_name[: 50] + "..."
        else:
            song_name = self.song.track_name

        while font1.size(song_name)[0] > self.dimension[0] - save_button_size - album_cover_size - margin * 2:
            font_size1 -= 1
            font1 = pygame.font.SysFont("Arial", font_size1, bold=True)

        while font2.size(artists)[0] > self.dimension[0] - save_button_size - album_cover_size - margin * 2:
            font_size2 -= 1
            font2 = pygame.font.SysFont("Arial", font_size2)

        #  if ever progressing with the project in the future,
        #  change this into an instance attribute and move it into playlist.load_display
        album_cover = Button("assets/album_cover.png",
                             (self.pos[0] + album_cover_size / 2 + margin - 20, self.pos[1] + self.dimension[1] / 2),
                             (album_cover_size, album_cover_size))

        text1 = font1.render(song_name, True, (30, 30, 30))
        text2 = font2.render(artists, True, (30, 30, 30))

        text1_rect = text1.get_rect(
            topleft=(
                album_cover.get_pos()[0] + album_cover_size / 2 + margin - 15,
                self.pos[1] + margin - 12
            )
        )
        text2_rect = text2.get_rect(topleft=(text1_rect.x, text1_rect.y + text1.get_height()))

        pygame.draw.rect(screen, "white", rect, border_radius=3)
        album_cover.draw(screen)
        self.button.draw(screen)
        screen.blit(text1, text1_rect)
        screen.blit(text2, text2_rect)

    def set_pos(self, pos: tuple) -> None:
        """Sets the potition"""
        self.pos = pos


class SongManager:
    """Class to load, parse, and manage the song data

    Instance Attributes:
    - 
    """
    _song_data_raw: list[dict[str, str]]
    _songs: dict[str, Song]

    def __init__(self, file_path: Optional[str] = None) -> None:
        """"""
        self._song_data_raw = []
        self._songs = {}

        if file_path is not None:
            self.load_data_raw(file_path)
            self.parse_data()

    def load_data_raw(self, file_path: str) -> None:
        """Loads the raw song data from a CSV file into the _song_data_raw attribute"""
        with open(file_path, 'r', encoding="utf-8") as file:
            csv_reader = DictReader(file)
            for row in csv_reader:
                self._song_data_raw.append(row)

    def parse_data(self) -> None:
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


@dataclass
class User:
    """A user class storing all useful login/registeration functions for quick referral.

    Instance Attributes:
        - name: A string of the name of user:
        - password: A string of the password of user
    """

    name: str
    password: str
    playlist: Playlist


class Accounts:
    """A manager class for user accounts"""
    _accounts: dict[str, User]

    def __init__(self, data_file: str) -> None:
        """Initialize accounts by reading data from appropriate account file"""
        self._accounts = self.load(data_file)

    @staticmethod
    def load(account_file: str) -> dict[str, User]:
        """Load account data from json data file into a dictionary mapping the username to user object"""

        with open(account_file, "r") as file:
            account_data = json.load(file)

        user_dict = {}
        song_data = SongManager()
        song_data.load_data_raw('dataset.csv')
        song_data.parse_data()

        for username in account_data:
            playlist = Playlist(username)

            for track_id in account_data[username]["playlist"]:
                playlist.add_song(song_data.get_song_by_id(track_id))

            user_obj = User(username, account_data[username]["password"], playlist)
            user_dict[username] = user_obj

        return user_dict

    def get_account(self, name: Optional[str] = None) -> dict[str, User] | User:
        """An accessor method used to access account object"""

        if name is None:
            return self._accounts
        else:
            return self._accounts[name]

    def get_all_name(self) -> set:
        """Return a set of all usernames"""
        return set(self._accounts.keys())

    def exist(self, username: str) -> bool:
        """Check if user exists via their username"""
        return username in self.get_all_name()

    def login(self, name: str, password: str) -> bool:
        """Check if name and passsword entered by user is the same as account info in database"""

        if name in self._accounts and password == self._accounts[name].password:
            return True
        else:
            return False

    def register(self, name: str, password: str) -> None:
        """Register a new account into the database with initial default game data"""

        self._accounts[name] = User(name, password, Playlist(name))

        account_data = {}

        for account in self._accounts:
            data = self._accounts[account]
            account_data[account] = {"password": data.password,
                                     "playlist": [song.track_id for song in
                                                  self._accounts[account].playlist.get_songs().values()]}

        with open("account_data.json", "w") as f:
            json.dump(account_data, f, indent=2)

    def save(self) -> None:
        """Saves account data into account database"""
        account_data = {}

        with open("account_data.json", "w") as f:
            for username in self._accounts:
                print(username + "playlist:", self._accounts[username])
                account_data[username] = {"password": self._accounts[username].password,
                                          "playlist":
                                              [song.track_id for song in
                                               self._accounts[username].playlist.get_songs().values()]
                                          }

            json.dump(account_data, f, indent=2)

    def handle_login(self, username: str) -> User | None:
        """A function to help manage the prompt message for user account info，
        Return user oject containing user info"""

        return self.get_account()[username]

    def error(self, username: str, password: str, re_password: str, get_message: Optional[bool] = None) -> bool | str:
        """Return whether error has occured, and if get_message, return the error message."""

        error_message = ""
        error = False

        if any(not item for item in [username, password, re_password]):
            error = True
            error_message = "Please fill out all boxes."

        elif len(username) < 2 or len(username) > 8:
            error = True
            error_message = "Username should be 2 to 8 characters long."

        elif len(password) < 5 or len(password) > 8:
            error = True
            error_message = "Password should be 5 to 8 characters long."

        elif any(" " in x for x in [username, password, re_password]):
            error = True
            error_message = "Empty spaces are not allowed in username or password."

        elif password != re_password:
            error = True
            error_message = "Passwords do not match."

        elif self.exist(username):
            error = True
            error_message = "Username is taken."

        if get_message:
            return error_message

        else:
            return error


if __name__ == '__main__':
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
