from constants import *

# intended to be expanded


class Classifier:
    def __init__(self, chillPlaylistName, upbeatPlaylistName):
        self.chillPlaylistName = chillPlaylistName
        self.upbeatPlaylistName = upbeatPlaylistName

    def getClassificationLabel(self, score):
        if score < CLASSIFICATION_LIMIT:
            return self.chillPlaylistName
        else:
            return self.upbeatPlaylistName

    def normalize(self, tempo):
        if tempo < MIN_TEMPO:
            tempo = MIN_TEMPO
        elif tempo > MAX_TEMPO:
            tempo = MAX_TEMPO
        return (tempo - MIN_TEMPO) / (MAX_TEMPO - MIN_TEMPO)

    def getClassification(self, energy, valence, danceability, tempo, acousticness):
        # normalize tempo
        tempo = self.normalize(tempo)

        # calculate score
        score = energy * ENERGY_WEIGHT + valence * VALENCE_WEIGHT + \
            danceability * DANCEABILITY_WEIGHT + tempo * \
            TEMPO_WEIGHT + (1.0-acousticness) * ACOUSTICNESS_WEIGHT

        score *= SCORE_SCALE

        return self.getClassificationLabel(score)
