import spotipy
from collections import defaultdict
from constants import *
from classifier import Classifier


class PlaylistGenerator:
    def __init__(
            self,
            spotipyClass,
            username,
            chillPlaylistName,
            midPlaylistName,
            upbeatPlaylistName,
            numSongsToClassify,
            overwritePlaylist):

        self.classifier = Classifier(
            chillPlaylistName, midPlaylistName, upbeatPlaylistName)
        self.spotipyClass = spotipyClass
        self.username = username
        self.numSongsToClassify = numSongsToClassify
        self.overwritePlaylist = overwritePlaylist
        self.chillPlaylistName = chillPlaylistName
        self.midPlaylistName = midPlaylistName
        self.upbeatPlaylistName = upbeatPlaylistName

    def generatePlaylists(self):
        songsToAdd = self.getTracksToAdd()
        songFeatures = self.getSongFeatures(songsToAdd)
        playlistMappingsToTracks = self.getPlaylistMappingsToTracks(
            songFeatures)

        exisitingPlaylistMappingsToIds = self.getExisitingPlaylistMappingsToIds()
        self.addTracksToPlaylist(
            playlistMappingsToTracks, exisitingPlaylistMappingsToIds)

    def getTracksToAdd(self):
        songsToAdd = []
        numSongsToGet = LIKED_SONG_MAX

        if self.numSongsToClassify < LIKED_SONG_MAX:
            numSongsToGet = self.numSongsToClassify

        # get songs in LIKED_SONG_MAX chunks
        batch_size = LIKED_SONG_MAX
        for offset in range(0, self.numSongsToClassify, LIKED_SONG_MAX):
            # reduce size if we are over self.numSongsToClassify
            if self.numSongsToClassify > offset and self.numSongsToClassify < offset + LIKED_SONG_MAX:
                batch_size = self.numSongsToClassify - offset
            songsToAdd += self.spotipyClass.current_user_saved_tracks(
                limit=batch_size, offset=offset)['items']

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
        playlistMap[self.chillPlaylistName] = []
        playlistMap[self.midPlaylistName] = []
        playlistMap[self.upbeatPlaylistName] = []

        for feature in songFeatures:
            tempo = feature['tempo']
            energy = feature['energy']
            valence = feature['valence']
            danceability = feature['danceability']
            acousticness = feature['acousticness']
            trackId = feature['id']

            playlist = self.classifier.getClassification(
                energy, valence, danceability, tempo, acousticness)
            playlistMap[playlist].append(trackId)

        return playlistMap

    def getExisitingPlaylistMappingsToIds(self):
        playlistsMap = {}
        exisitingPlaylists = []

        exisitingPlaylistObjects = self.spotipyClass.user_playlists(
            user=self.username, limit=PLAYLISTS_REQUEST_MAX, offset=0)
        exisitingPlaylists += exisitingPlaylistObjects['items']

        # in case user has more than PLAYLISTS_REQUEST_MAX playlists, request in PLAYLISTS_REQUEST_MAX
        # size chunks
        totalNumPlaylists = exisitingPlaylistObjects['total']
        for offset in range(PLAYLISTS_REQUEST_MAX, totalNumPlaylists, PLAYLISTS_REQUEST_MAX):
            exisitingPlaylistObjects = self.spotipyClass.user_playlists(
                user=self.username, limit=PLAYLISTS_REQUEST_MAX, offset=offset)
            exisitingPlaylists += exisitingPlaylistObjects['items']

        for playlist in exisitingPlaylists:
            name = playlist['name']
            playlistId = playlist['id']
            playlistsMap[name] = playlistId

        return playlistsMap

    # Get a list of trackIds in the playlist (spotify max limit to return is 100)

    def getExistingTracksIdsInPlaylist(self, playlistId):
        existingTracks = []

        existingTrackObjects = self.spotipyClass.user_playlist_tracks(
            user=self.username, playlist_id=playlistId, limit=TRACKS_IN_PLAYLIST_REQUEST_MAX, offset=0)
        existingTracks += existingTrackObjects['items']

        # in case user has more than TRACKS_IN_PLAYLIST_REQUEST_MAX tracks in this playlist,
        # request in TRACKS_IN_PLAYLIST_REQUEST_MAX size chunks
        totalNumTracks = existingTrackObjects['total']
        for offset in range(TRACKS_IN_PLAYLIST_REQUEST_MAX, totalNumTracks, TRACKS_IN_PLAYLIST_REQUEST_MAX):
            existingTrackObjects = self.spotipyClass.user_playlist_tracks(
                user=self.username, playlist_id=playlistId, limit=TRACKS_IN_PLAYLIST_REQUEST_MAX, offset=offset)
            existingTracks += existingTrackObjects['items']

        trackIds = []
        for track in existingTracks:
            trackIds.append(track['track']['id'])

        return trackIds

    def removeTracksInPlaylist(self, playlistId, tracksToRemove):
        for offset in range(0, len(tracksToRemove), TRACKS_TO_REMOVE_REQUEST_MAX):
            resultAdd = self.spotipyClass.user_playlist_remove_all_occurrences_of_tracks(
                user=self.username,
                playlist_id=playlistId,
                tracks=tracksToRemove[offset:min(offset + TRACKS_TO_REMOVE_REQUEST_MAX, len(tracksToRemove))])

    def createNewPlaylist(self, playlist):
        newPlaylist = self.spotipyClass.user_playlist_create(
            user=self.username, name=playlist, public=CREATE_PUBLIC_PLAYLISTS)
        return newPlaylist['id']

    def addTracksToPlaylist(self, playlistMappingsToTracks, exisitingPlaylistMappingsToIds):
        for playlist, trackIds in playlistMappingsToTracks.items():
            if playlist in exisitingPlaylistMappingsToIds.keys():
                playlistId = exisitingPlaylistMappingsToIds[playlist]
            else:
                playlistId = self.createNewPlaylist(playlist)

            existingTracks = self.getExistingTracksIdsInPlaylist(playlistId)

            # overwrite playlist
            if self.overwritePlaylist:
                self.removeTracksInPlaylist(playlistId, existingTracks)
                existingTracks = []

            trackIdsToAdd = []
            for trackId in trackIds:
                if trackId not in existingTracks:
                    trackIdsToAdd.append(trackId)

            if len(trackIdsToAdd) > 0:
                for offset in range(0, len(trackIdsToAdd), TRACKS_TO_ADD_REQUEST_MAX):
                    resultAdd = self.spotipyClass.user_playlist_add_tracks(
                        user=self.username,
                        playlist_id=playlistId,
                        tracks=trackIdsToAdd[offset:min(offset+TRACKS_TO_ADD_REQUEST_MAX, len(trackIdsToAdd))])
