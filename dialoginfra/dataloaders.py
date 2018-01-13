"""This module provides a set of basic dataloaders for different chatbot types:

    ``DataLoader(object)``
    base class for all data loader types, implements the ``load()`` method
    which constructs data-structures to store utterances and other associated properties.
    These properties are pre-defined with the format of a dataset.

    ``JsonDataLoader(DataLoader)``

    ``FbDataLoader(DataLoader)``:


"""

import json as jp
from .episodeformats import Episode, create_episodes

class DataLoader(object):
    def __init__(self, filepath, datafmt):
        self.filepath = filepath
        self.datafmt = datafmt

    def load(self):
        pass

    def validate(self):
        pass

class JsonDataLoader(DataLoader):
    def load(self):
        parsedEpisodes = []
        with open(self.filepath) as json_data:
            episode_data = jp.load(json_data)
            parsedEpisodes = create_episodes(episode_data, self.datafmt)
        # except:
        #     print("invalid json format")
        return  parsedEpisodes

class FbDataLoader(DataLoader):
    """
    The way FB Dialog data is set up is as follows:

    ::

        1 Sam went to the kitchen.
        2 Pat gave Sam the milk.
        3 Where is the milk?<TAB>kitchen<TAB>1<TAB>hallway|kitchen|bathroom
        4 Sam went to the hallway
        5 Pat went to the bathroom
        6 Where is the milk?<TAB>hallway<TAB>1<TAB>hallway|kitchen|bathroom

    Lines 1-6 represent a single episode, with two different examples: the first
    example is lines 1-3, and the second is lines 4-6.

    Lines 1,2,4, and 5 represent contextual information.

    Lines 3 and 6 contain a query, a label, a reward for getting the question
    correct, and three label candidates.

    Since both of these examples are part of the same episode, the information
    provided in the first example is relevant to the query in the second example
    and therefore the agent must remember the first example in order to do well.

    In general dialog in this format can be any speech, not just QA pairs:

    ::

        1 Hi how's it going?<TAB>It's going great. What's new?
        2 Well I'm working on a new project at work.<TAB>Oh me too!
        3 Oh cool!<TAB>Tell me about yours.

    etc.
    """

