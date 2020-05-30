import os

# feature weights
ENERGY_WEIGHT = 0.3
VALENCE_WEIGHT = 0.1
DANCEABILITY_WEIGHT = 0.3
TEMPO_WEIGHT = 0.1
ACOUSTICNESS_WEIGHT = 0.2

# playlist names
ULTRA_CHILL_PLAYLIST = "ultra chill (#generated)"
CHILL_PLAYLIST = "chill (#generated)"
UPBEAT_PLAYLIST = "upbeat (#generated)"

# normalize constants
MAX_TEMPO = 180.0
MIN_TEMPO = 60.0

# score limit for classifications
MID_CLASSIFICATION_LIMIT = 5
UPBEAT_CLASSIFICATION_LIMIT = 7

# how much to scale the score by
SCORE_SCALE = 10.0

# spotify security scopes
SCOPE = 'user-library-read playlist-read-private playlist-modify-private playlist-modify-public'

# max request limits for spotify
LIKED_SONG_MAX = 20
FEATURES_REQUEST_MAX = 50
PLAYLISTS_REQUEST_MAX = 50
TRACKS_IN_PLAYLIST_REQUEST_MAX = 100
TRACKS_TO_ADD_REQUEST_MAX = 100
TRACKS_TO_REMOVE_REQUEST_MAX = 100

# whether to create new playlists as public
CREATE_PUBLIC_PLAYLISTS = True

# Server-side Parameters
PORT = os.environ['PORT']

# spotify app credentials
SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
SPOTIFY_REDIRECT_URL = os.environ['SPOTIFY_REDIRECT_URL']
SSK = os.environ['SSK']
