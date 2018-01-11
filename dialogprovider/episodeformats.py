def create_episodes(episode_data, dataformat):
    parsedEpisodes = []
    for episode in episode_data:
        if dataformat == "JsonBasic":
            jsonBasicEpisode = JsonBasicEpisode(episode)
            parsedEpisodes.append(jsonBasicEpisode)
        elif dataformat == "JsonTuring":
            jsonTuringEpisode = JsonTuringEpisode(episode)
            parsedEpisodes.append(jsonTuringEpisode)
        else:
            pass
    return parsedEpisodes

class Episode(object):
    def __init__(self, episodeDetails):
        if not hasattr(episodeDetails, 'episodeId') and \
            hasattr(episodeDetails, 'thread') and \
            hasattr(episodeDetails, 'timestamp'):
            raise AttributeError("EpisodeId or \
                other mandatory parameter are missing in Episode Details.")
        self.episodeId = episodeDetails['episodeId']
        self.timestamp = episodeDetails['timestamp']

class JsonBasicEpisode(Episode):
    def __init__(self, episodeDetails):
        super().__init__(self, episodeDetails)
        for thread in episodeDetails['thread']:
            self.thread.append(Thread(thread))

class JsonTuringEpisode(Episode):
    def __init__(self, episodeDetails):
        if 'dialogId' in episodeDetails:
            self.dialogId = episodeDetails['dialogId']
        if 'evaluation' in episodeDetails:
            self.evaluation = []
            for evaluationValues in episodeDetails['evaluation']:
                self.evaluation.append(Evaluation(evaluationValues))
        if 'users' in episodeDetails:
            self.users = []
            for userDetails in episodeDetails['users']:
                self.users.append(User(userDetails))
        if 'thread' in episodeDetails:
            self.thread = []
            for utterance in episodeDetails['thread']:
                self.thread.append(Utterance(utterance))
        if 'context' in episodeDetails:
            self.context = episodeDetails['context']

# TODO: use **kwargs instead of assigning separately

class Evaluation(object):
    def __init__(self, properties):
        self.breadth = properties['breadth']
        self.userId = properties['userId']
        self.engagement = properties['engagement']
        self.quality = properties['quality']

class User(object):
    def __init__(self, properties):
        self.userType = properties['userType']
        self.id = properties['id']

class Utterance(object):
    def __init__(self, properties):
        if not hasattr(properties, 'userId') and \
            hasattr(properties, 'text'):
            raise AttributeError("UserId or \
                other mandatory parameter are missing in Utterance Details.")
        self.userId = properties['userId']
        self.text = properties['text']