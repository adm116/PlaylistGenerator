import spotipy
import random
from collections import defaultdict
from constants import *
from classifier import Classifier

class PlaylistGenerator:
    def __init__(
            self,
            spotipyClass,
            username,
            maxNumTracks):

        self.classifier = Classifier(ULTRA_CHILL_PLAYLIST, CHILL_PLAYLIST, UPBEAT_PLAYLIST)
        self.playlistNames = [ULTRA_CHILL_PLAYLIST, CHILL_PLAYLIST, UPBEAT_PLAYLIST]
        self.spotipyClass = spotipyClass
        self.username = username
        self.maxNumTracks = maxNumTracks

    def generatePlaylists(self):
        # get all liked songs and shuffle them
        songsToAdd = self.getTracksToAdd()
        random.shuffle(songsToAdd)

        # map songs to playlists
        songFeatures = self.getSongFeatures(songsToAdd)
        playlistMappingsToTracks = self.getPlaylistMappingsToTracks(songFeatures)

        # remove existing matching playlists, create playlists, and add songs
        self.removeExistingMatchingPlaylists()
        self.addTracksToPlaylist(playlistMappingsToTracks)

    def getExistingPlaylists(self):
        exisitingPlaylists = []

        exisitingPlaylistObjects = self.spotipyClass.user_playlists(
            user=self.username, limit=PLAYLISTS_REQUEST_MAX, offset=0)
        exisitingPlaylists += exisitingPlaylistObjects['items']

        # in case user has more than PLAYLISTS_REQUEST_MAX playlists, request in PLAYLISTS_REQUEST_MAX
        # sized chunks
        totalNumPlaylists = exisitingPlaylistObjects['total']
        for offset in range(PLAYLISTS_REQUEST_MAX, totalNumPlaylists, PLAYLISTS_REQUEST_MAX):
            exisitingPlaylistObjects = self.spotipyClass.user_playlists(
                user=self.username, limit=PLAYLISTS_REQUEST_MAX, offset=offset)
            exisitingPlaylists += exisitingPlaylistObjects['items']

        return exisitingPlaylists

    def getTracksToAdd(self):
        songsToAdd = []

        response = self.spotipyClass.current_user_saved_tracks(limit=LIKED_SONG_MAX, offset=0)
        songsToAdd += response['items']

        # in case user has more than LIKED_SONG_MAX liked songs, request in LIKED_SONG_MAX sized chunks
        totalNumLikedSongs = response['total']
        for offset in range(LIKED_SONG_MAX, totalNumLikedSongs, LIKED_SONG_MAX):
            response = self.spotipyClass.current_user_saved_tracks(limit=LIKED_SONG_MAX, offset=offset)
            songsToAdd += response['items']

        return songsToAdd

    def getSongFeatures(self, tracks):
        features = []

        for offset in range(0, len(tracks), FEATURES_REQUEST_MAX):
            songFeaturesToRequest = []

            # divide into FEATURES_REQUEST_MAX size chunks
            for track in tracks[offset:offset + FEATURES_REQUEST_MAX]:
                songFeaturesToRequest.append(track['track']['id'])

            features += self.spotipyClass.audio_features(
                tracks=songFeaturesToRequest)

        return features

    def getPlaylistMappingsToTracks(self, songFeatures):
        # initialize playlist names with empty tracks
        playlistMap = defaultdict(list)
        playlistMap[ULTRA_CHILL_PLAYLIST] = []
        playlistMap[CHILL_PLAYLIST] = []
        playlistMap[UPBEAT_PLAYLIST] = []

        for feature in songFeatures:
            tempo = feature['tempo']
            energy = feature['energy']
            valence = feature['valence']
            danceability = feature['danceability']
            acousticness = feature['acousticness']
            trackId = feature['id']

            playlist = self.classifier.getClassification(
                energy, valence, danceability, tempo, acousticness)
            
            # only take maxNumTracks
            if len(playlistMap[playlist]) < self.maxNumTracks:
                playlistMap[playlist].append(trackId)

        return playlistMap

    def removeExistingMatchingPlaylists(self):
        # we have to go through all user playlists to check for a playlist name match
        exisitingPlaylists = self.getExistingPlaylists()
        for playlist in exisitingPlaylists:
            name = playlist['name']
            playlistId = playlist['id']

            if name in self.playlistNames:
                self.spotipyClass.user_playlist_unfollow(user=self.username, playlist_id=playlistId)

    def createNewPlaylist(self, playlist):
        newPlaylist = self.spotipyClass.user_playlist_create(
            user=self.username, name=playlist, public=CREATE_PUBLIC_PLAYLISTS)
        return newPlaylist['id']

    def addTracksToPlaylist(self, playlistMappingsToTracks):
        for playlist, trackIds in playlistMappingsToTracks.items():
            playlistId = self.createNewPlaylist(playlist)

            if len(trackIds) > 0:
                for offset in range(0, len(trackIds), TRACKS_TO_ADD_REQUEST_MAX):
                    self.spotipyClass.user_playlist_add_tracks(
                        user=self.username,
                        playlist_id=playlistId,
                        tracks=trackIds[offset:min(offset+TRACKS_TO_ADD_REQUEST_MAX, len(trackIds))])