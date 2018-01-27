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
        if not ('thread' in episodeDetails and
                'participantData' in episodeDetails):
            raise AttributeError("Mandatory parameters missing in Episode Details.")
        self.participantData = ParticipantData(episodeDetails['participantData'])
        self.thread = []

class JsonBasicEpisode(Episode):
    def __init__(self, episodeDetails):
        super().__init__(episodeDetails)
        for utterance in episodeDetails['thread']:
            self.thread.append(Utterance(utterance))

class JsonHangoutEpisodes(Episode):
    def __init__(self, episodeDetails):
        super().__init__(episodeDetails)
        self.type = episodeDetails['type']
        for utterance in episodeDetails['thread']:
            self.thread.append(HangoutUtterance(utterance))

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
        if not ('userId' in properties and
            'text' in properties and
            'timestamp' in properties):
            raise AttributeError("UserId or \
                other mandatory parameter are missing in Utterance Details.")
        self.utterance = {'userId':properties['userId'],
                          'text':properties['text'],
                          'timestamp':properties['timestamp']}

class HangoutUtterance(Utterance):
    def __init__(self,properties):
        super.__init__(properties)
        if not 'utteranceId' in properties:
            raise AttributeError("HangoutUtterance mandatory parameters missing!.")
        self.utterance['utteranceId'] = properties['utteranceId']

class ParticipantData(object):
    def __init__(self, participantData):
        self.participantDetails = []
        for participantDetails in participantData:
            if not ('userId' in participantDetails and
                    'userName' in participantDetails):
                raise AttributeError("Mandatory parameters missing in Participant Data.")
            self.participantDetails.append({'userId':participantDetails['userId'],
                                            'userName': participantDetails['userName']})