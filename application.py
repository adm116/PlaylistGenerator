from flask import Flask, render_template, redirect, request, session, make_response, session, redirect
from constants import *
from playlistGenerator import PlaylistGenerator
import spotipy
import time

app = Flask(__name__)
app.secret_key = SSK


@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/")
def verify():
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT_URL, scope=SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route("/callback")
def callback():
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT_URL, scope=SCOPE)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code=code, check_cache=False)

    # Saving the access token along with all other token related info
    session["token_info"] = token_info
    return redirect("index")


@app.route("/generatePlaylists", methods=['POST'])
def generatePlaylists():
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')

    data = request.form
    chillPlaylistName = data['chillPlaylistName']
    midPlaylistName = data['midPlaylistName']
    upbeatPlaylistName = data['upbeatPlaylistName']
    numSongsToClassify = int(data['numTracks'])
    overwritePlaylist = bool(data.get('overwritePlaylist'))
    maxNumTracks = int(data['maxNumTracks'])

    spotipyClass = spotipy.Spotify(
        auth=session.get('token_info').get('access_token'))
    currentUser = spotipyClass.current_user()
    currentUsername = currentUser['id']

    generator = PlaylistGenerator(
        spotipyClass,
        currentUsername,
        chillPlaylistName,
        midPlaylistName,
        upbeatPlaylistName,
        numSongsToClassify,
        overwritePlaylist,
        maxNumTracks)
    generator.generatePlaylists()

    return render_template('index.html', showSuccess=True)

# Checks to see if token is valid and gets a new token if not


def get_token(session):
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
        sp_oauth = spotipy.oauth2.SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT_URL, scope=SCOPE)
        token_info = sp_oauth.refresh_access_token(
            session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
