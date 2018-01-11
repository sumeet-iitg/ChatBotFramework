from dataloaders import JsonDataLoader
from episodeformats import Utterance
import json

class DialogProvider(object):
    def __init__(self, platFormId, sessionId, activeLogFilePath):
        self.state = -1
        self.platFormId = platFormId
        self.sessionId = sessionId
        self.activeLogFilePath = activeLogFilePath

    def InitializeDialogProvider(self, savedLogFilePath):
        self.__processLogFile(self, savedLogFilePath)

    def __processLogFile(self, logFilePath):
        jsonLoader = JsonDataLoader(logFilePath, "JsonBasic")
        self.episodes = jsonLoader.load()
        # copy the state information from the episode
        # TODO: build state into utterances rather than episodes
        if hasattr(self.episodes[-1], 'state'):
            self.state = self.episodes[-1].state

    def UpdateJson(self, utterance, state):
        latestThread = self.episodes[-1].thread
        latestThread.append(Utterance(utterance))
        self.state = state

    def PersistJson(self):
        with open(self.activeLogFilePath, 'w', encoding='utf-8') as jsonFp:
            json.dump(self.episodes, jsonFp)
