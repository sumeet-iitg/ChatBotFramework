from .dataloaders import JsonDataLoader
from .episodeformats import Utterance
import json


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        # return {'__{}__'.format(o.__class__.__name__): o.__dict__}
        jsonOut = o.__dict__
        return  jsonOut

class DialogProvider(object):
    def __init__(self, platformId, sessionId, activeLogFilePath):
        self.state = 'NA'
        self.platformId = platformId
        self.sessionId = sessionId
        self.activeLogFilePath = activeLogFilePath

    def InitializeDialogProvider(self, savedLogFilePath, fmt = "JsonBasic"):
        self.__processLogFile(savedLogFilePath, fmt)

    def __processLogFile(self, logFilePath, fmt):
        jsonLoader = JsonDataLoader(logFilePath, fmt)
        self.episodes = jsonLoader.load()
        # copy the state information from the episode
        # TODO: build state into utterances rather than episodes
        if hasattr(self.episodes[-1], 'state'):
            self.state = self.episodes[-1].state

    def UpdateJson(self, utterance, state = -1):
        latestThread = self.episodes[-1].thread
        latestThread.append(Utterance(utterance))
        if not state == -1:
            self.state = state

    def PersistJson(self):
        with open(self.activeLogFilePath, 'w', encoding='utf-8') as jsonFp:
            json.dump(self, jsonFp, cls=CustomEncoder, indent=2)
