import sys
import spotipy
from constants import *
from playlistGenerator import PlaylistGenerator

# arguments
username = sys.argv[1]
numSongsToClassify = int(sys.argv[2])

token = spotipy.util.prompt_for_user_token(
    username,
    SCOPE,
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URL)

if token:
    spotipyClass = spotipy.Spotify(auth=token)
    spotipyClass.trace = False
    generator = PlaylistGenerator(spotipyClass, username, numSongsToClassify)
    generator.generatePlaylists()
else:
    print("Can't get token for", username)
