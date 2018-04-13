"""
This file defines the control mechanism to rank the slots
"""

from nltk.tag.stanford import StanfordNERTagger
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from sutime import SUTime
from constants import INTENT_TYPES, GREET_TERMS, CLOSURE_TERMS, WEATHER_TERMS, YES_TERMS, NO_TERMS, TIME_ABRV,DAY_TERMS
import datetime


class NLUModule:
    def __init__(self, classifier_path=None, ner_path = None, sutime_jar_path = None):
        # Change the path according to your system
        if classifier_path is None:
            classifier_path = "C:\stanford_corenlp\stanford-ner-2018-02-27\stanford-ner-2018-02-27\classifiers\english.muc.7class.distsim.crf.ser.gz"

        if ner_path is None:
            ner_path = "C:\stanford_corenlp\stanford-ner-2018-02-27\stanford-ner-2018-02-27\stanford-ner.jar"

        if sutime_jar_path is None:
            sutime_jar_path = "C:\stanford_corenlp\stanford-corenlp-full-2018-02-27\stanford-corenlp-full-2018-02-27"

        self.stanford_classifier = classifier_path
        self.stanford_ner_path = ner_path
        self.sutime_path = sutime_jar_path

        # Creating Tagger Object
        self.st = StanfordNERTagger(self.stanford_classifier, self.stanford_ner_path)
        self.su = SUTime(jars=self.sutime_path, mark_time_ranges=True, include_range=True)

        self.weather_terms = ["weather", "climate", "precipitation", "sun", "rain", "cloud","snow", "hot", "humid", "cold", "sunny", "windy","cloudy",
                              "rainy", "snowy", "misty", "foggy", "colder","hotter", "warmer", "pleasant"]
        self.greet_terms= ["hello","hey","howdy","hello","hi", "yo", "yaw"]
        self.closure_terms = ["no", "nope", "thank you", "bye", "tata", "thanks", "that will be all", "that's it", "that'll be all"]
        self.day_terms = ["dawn", "dusk", "morning", "evening", "noon","afternoon", "night", "tonight", "midnight", "midday"] #, "hours"]
        self.date_terms = ["today", "tomorrow", "yesterday"]

    def DiscoverIntentAndEntities(self, text):
        tokenized_text = word_tokenize(text)
        classified_text = self.st.tag(tokenized_text)
        time_tags = self.su.parse(text)
        queryDate = None
        queryTime = None
        # pos_tags = pos_tag(tokenized_text)

        detectionResults = {"intent":INTENT_TYPES.UNK, "entities":{"LOCATION":"", "DATE":[], "TIME":[], "DURATION":[], "QUERIES":[]}}
        returnIntentAndEnt = {"intent":INTENT_TYPES.UNK, "entities":{"LOCATION":"", "DATE":"", "TIME":""}}

        for word,tag in classified_text:
            if 'LOCATION' in tag:
                detectionResults["entities"]["LOCATION"] += word + " "
            # elif 'DATE' in tag or word in self.date_terms:
            #     detectionResults["entities"]["DATE"] = word + " "
            # elif 'DATE' in tag or word in self.day_terms:
            #     detectionResults["entities"]["HOUR"] = word + " "
            elif 'O' in tag and word in WEATHER_TERMS:
                detectionResults["entities"]["QUERIES"].append(word)
                detectionResults["intent"] = INTENT_TYPES.WTH_QU

        if len(time_tags) > 0:
            for tag in time_tags:
                typeKey = tag["type"]
                detectionResults["entities"][typeKey].append(tag["value"])
            if len(detectionResults["entities"]["DATE"]) > 0:
                for dateVal in detectionResults["entities"]["DATE"]:
                    queryDate = dateVal
                    if 'W' in dateVal:
                        queryDate = dateVal.replace('W','')

            if len(detectionResults["entities"]["TIME"]) > 0:
                for timeVal in detectionResults["entities"]["TIME"]:
                    timeTokens = timeVal.split('T')
                    if not queryDate is None:
                        queryDate = timeTokens[0]
                    timePart = timeTokens[1]

                    if timePart in TIME_ABRV.keys():
                        timePart = DAY_TERMS[TIME_ABRV[timePart]]
                        # Overwrite the query time with a generic time maps for MO, AF etc.
                        queryTime = timePart

                    #Do not overwrite query time if some time was detected already
                    if not queryTime is None:
                        queryTime = timePart

        if detectionResults["intent"] == INTENT_TYPES.UNK:
            if text in GREET_TERMS:
                detectionResults["intent"] = INTENT_TYPES.GRT
            elif text in CLOSURE_TERMS:
                detectionResults["intent"] = INTENT_TYPES.CLS
            elif text in YES_TERMS:
                detectionResults["intent"] = INTENT_TYPES.ANS_YES
            elif text in NO_TERMS:
                detectionResults["intent"] = INTENT_TYPES.ANS_NO

        if len(detectionResults["entities"]["LOCATION"]) > 0 or len(detectionResults["entities"]["DATE"]) \
                or len(detectionResults["entities"]["TIME"]) or len(detectionResults["entities"]["DURATION"]) > 0:
            detectionResults["intent"] = INTENT_TYPES.ANS_SLT

        returnIntentAndEnt["intent"] = detectionResults["intent"]
        if not queryDate is None:
            returnIntentAndEnt["entities"]["DATE"] = queryDate
        if not queryTime is None:
            returnIntentAndEnt["entities"]["TIME"] = queryTime

        return returnIntentAndEnt

# nlu = NLUModule()
# print(nlu.DiscoverIntentAndEntities("How is the weather on Fifth March."))
# print(nlu.DiscoverIntentAndEntities("How is the weather in March."))
# print(nlu.DiscoverIntentAndEntities("What is it like on Tuesday."))
# print(nlu.DiscoverIntentAndEntities("How does it look like tomorrow?"))
# print(nlu.DiscoverIntentAndEntities("What is the weather like next week?"))
# print(nlu.DiscoverIntentAndEntities("What is it like tomorrow between 3 to 4pm ?"))
# print(nlu.DiscoverIntentAndEntities("What is it like tomorrow afternoon?"))
# print(nlu.DiscoverIntentAndEntities("What is it like tomorrow at noon?"))
# print(nlu.DiscoverIntentAndEntities("What is it like tomorrow evening?"))
# print(nlu.DiscoverIntentAndEntities("What is it like tomorrow morning?"))
# print(nlu.DiscoverIntentAndEntities("What is it like tomorrow night?"))
# print(nlu.DiscoverIntentAndEntities("What is it like tomorrow at midnight?"))
# print(nlu.DiscoverIntentAndEntities("What is it like tomorrow during noon?"))
# print(nlu.DiscoverIntentAndEntities("What is it like tomorrow around 11:00 in the morning?"))
# print(nlu.DiscoverIntentAndEntities("What is it like next Tuesday around 11:00 in the morning?"))
# print(nlu.DiscoverIntentAndEntities("What is it like next Tuesday between 10:00 and 11:00 in the night?"))

# from nltk import word_tokenize, pos_tag, ne_chunk
#
# import os
# import collections
#
# from nltk.stem.snowball import SnowballStemmer
# from nltk.chunk import conlltags2tree, tree2conlltags
# import string
#
#
# def features(tokens, index, history):
#     """
#     `tokens`  = a POS-tagged sentence [(w1, t1), ...]
#     `index`   = the index of the token we want to extract features for
#     `history` = the previous predicted IOB tags
#     """
#
#     # init the stemmer
#     stemmer = SnowballStemmer('english')
#
#     # Pad the sequence with placeholders
#     tokens = [('[START2]', '[START2]'), ('[START1]', '[START1]')] + list(tokens) + [('[END1]', '[END1]'),
#                                                                                     ('[END2]', '[END2]')]
#     history = ['[START2]', '[START1]'] + list(history)
#
#     # shift the index with 2, to accommodate the padding
#     index += 2
#
#     word, pos = tokens[index]
#     prevword, prevpos = tokens[index - 1]
#     prevprevword, prevprevpos = tokens[index - 2]
#     nextword, nextpos = tokens[index + 1]
#     nextnextword, nextnextpos = tokens[index + 2]
#     previob = history[index - 1]
#     contains_dash = '-' in word
#     contains_dot = '.' in word
#     allascii = all([True for c in word if c in string.ascii_lowercase])
#
#     allcaps = word == word.capitalize()
#     capitalized = word[0] in string.ascii_uppercase
#
#     prevallcaps = prevword == prevword.capitalize()
#     prevcapitalized = prevword[0] in string.ascii_uppercase
#
#     nextallcaps = prevword == prevword.capitalize()
#     nextcapitalized = prevword[0] in string.ascii_uppercase
#
#     return {
#         'word': word,
#         'lemma': stemmer.stem(word),
#         'pos': pos,
#         'all-ascii': allascii,
#
#         'next-word': nextword,
#         'next-lemma': stemmer.stem(nextword),
#         'next-pos': nextpos,
#
#         'next-next-word': nextnextword,
#         'nextnextpos': nextnextpos,
#
#         'prev-word': prevword,
#         'prev-lemma': stemmer.stem(prevword),
#         'prev-pos': prevpos,
#
#         'prev-prev-word': prevprevword,
#         'prev-prev-pos': prevprevpos,
#
#         'prev-iob': previob,
#
#         'contains-dash': contains_dash,
#         'contains-dot': contains_dot,
#
#         'all-caps': allcaps,
#         'capitalized': capitalized,
#
#         'prev-all-caps': prevallcaps,
#         'prev-capitalized': prevcapitalized,
#
#         'next-all-caps': nextallcaps,
#         'next-capitalized': nextcapitalized,
#     }
#
# def to_conll_iob(annotated_sentence):
#     """
#     `annotated_sentence` = list of triplets [(w1, t1, iob1), ...]
#     Transform a pseudo-IOB notation: O, PERSON, PERSON, O, O, LOCATION, O
#     to proper IOB notation: O, B-PERSON, I-PERSON, O, O, B-LOCATION, O
#     """
#     proper_iob_tokens = []
#     for idx, annotated_token in enumerate(annotated_sentence):
#         tag, word, ner = annotated_token
#
#         if ner != 'O':
#             if idx == 0:
#                 ner = "B-" + ner
#             elif annotated_sentence[idx - 1][2] == ner:
#                 ner = "I-" + ner
#             else:
#                 ner = "B-" + ner
#         proper_iob_tokens.append((tag, word, ner))
#     return proper_iob_tokens
#
#
# def read_gmb(corpus_root):
#     for root, dirs, files in os.walk(corpus_root):
#         for filename in files:
#             if filename.endswith(".tags"):
#                 with open(os.path.join(root, filename), 'rb') as file_handle:
#                     file_content = file_handle.read().decode('utf-8').strip()
#                     annotated_sentences = file_content.split('\n\n')
#                     for annotated_sentence in annotated_sentences:
#                         annotated_tokens = [seq for seq in annotated_sentence.split('\n') if seq]
#
#                         standard_form_tokens = []
#
#                         for idx, annotated_token in enumerate(annotated_tokens):
#                             annotations = annotated_token.split('\t')
#                             word, tag, ner = annotations[0], annotations[1], annotations[3]
#
#                             if ner != 'O':
#                                 ner = ner.split('-')[0]
#
#                             if tag in ('LQU', 'RQU'):  # Make it NLTK compatible
#                                 tag = "``"
#
#                             standard_form_tokens.append((word, tag, ner))
#
#                         conll_tokens = to_conll_iob(standard_form_tokens)
#
#                         # Make it NLTK Classifier compatible - [(w1, t1, iob1), ...] to [((w1, t1), iob1), ...]
#                         # Because the classfier expects a tuple as input, first item input, second the class
#                         yield [((w, t), iob) for w, t, iob in conll_tokens]
#
#
# import pickle
# from collections import Iterable
# from nltk.tag import ClassifierBasedTagger
# from nltk.chunk import ChunkParserI
#
#
# class NamedEntityChunker(ChunkParserI):
#     def __init__(self, train_sents, **kwargs):
#         assert isinstance(train_sents, Iterable)
#
#         self.feature_detector = features
#         self.tagger = ClassifierBasedTagger(
#             train=train_sents,
#             feature_detector=features,
#             **kwargs)
#
#     def parse(self, tagged_sent):
#         chunks = self.tagger.tag(tagged_sent)
#
#         # Transform the result from [((w1, t1), iob1), ...]
#         # to the preferred list of triplets format [(w1, t1, iob1), ...]
#         iob_triplets = [(w, t, c) for ((w, t), c) in chunks]
#
#         # Transform the list of triplets to nltk.Tree format
#         return conlltags2tree(iob_triplets)
#
#
# corpus_root = "gmb-2.2.0/gmb-2.2.0"  # Make sure you set the proper path to the unzipped corpus
# reader = read_gmb(corpus_root)
# training_samples = list(reader)
# chunker = NamedEntityChunker(training_samples[:2000])
# print(chunker.parse(pos_tag(word_tokenize("What's the weather like in Pittsburgh this Monday."))))