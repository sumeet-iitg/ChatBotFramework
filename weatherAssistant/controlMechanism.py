"""
This file defines the control mechanism to rank the slots
"""
from speechToText import speech_to_text
from textToSpeech import text_to_speech
from ner_extractor import NLUModule, basic_intent_types
from constants import WEATHER_TERMS, GREET_TERMS, DATE_TERMS, CLOSURE_TERMS, DAY_TERMS, DAY_OF_WEEK
import datetime

def locationExtractor(intentAndEntityDict):
    locationVal = intentAndEntityDict["entities"]["LOCATION"]
    return locationVal

def timeExtractor(intentAndEntityDict):
    dateVal = intentAndEntityDict["entities"]["DATE"]
    timeVal = intentAndEntityDict["entities"]["HOUR"]
    dateToday = datetime.datetime.today()
    hours = -1
    if timeVal in DAY_TERMS.keys():
        hours = int(DAY_TERMS[timeVal].split(":")[0])
    addDays = 0
    if dateVal in DAY_OF_WEEK.keys():
        if DAY_OF_WEEK[dateVal] >= dateToday.weekday():
            addDays = DAY_OF_WEEK[dateVal] - dateToday.weekday()
        else:
            addDays = DAY_OF_WEEK[dateVal] + 7 - dateToday.weekday()
    elif dateVal in DATE_TERMS.keys():
        addDays = DATE_TERMS[dateVal]

    queryDate = dateToday + datetime.timedelta(days=addDays)
    if not hours == -1:
        queryDate = datetime.datetime(queryDate.year, queryDate.month, queryDate.day, hours)
    return queryDate

def locationValidation(location):
    return True

def timeValidation():
    return True

class slot:
    def __init__(self, slotName, slotQuestion, slotValidationFunction, slotValueExtractor):
        self.slotName = slotName
        self.slotValue = ""
        self.slotQuestion = slotQuestion
        self.slotValidationFunction = slotValidationFunction
        self.slotValueExtractor = slotValueExtractor

# Class to represent a form in dialog systems
# A form has slot names and associated questions
# For each empty slot, the system asks the necessary question
class form:
    def __init__(self, slots):
        self.emptySlots = slots
        self.filledSlots = []

    def getNextEmptySlot(self):
        slot_obj = None
        if len(self.emptySlots) > 0:
            slot_obj = self.emptySlots[0]
        return slot_obj

    def fillEmptySlot(self, slot_obj):
        self.filledSlots.append(slot_obj)
        del self.emptySlots[0]

# Class for building context in form filler dialog systems
class form_filler:
    def __init__(self, form, retryCount):
        self.form = form
        self.retryCount = retryCount
        self.nluModule = NLUModule()

    # Fills the form by asking the user for each slot
    # while validating the provided values
    # In case of invalid values it asks the user again.
    def fill_form(self):
        slot_obj = self.form.getNextEmptySlot()
        while not slot_obj is None:
            text_to_speech(slot_obj.slotQuestion)
            user_text = speech_to_text()
            retry = 0
            while retry < self.retryCount:
                intentAndEntitiesDict = self.nluModule.DiscoverIntentAndEntities(user_text)
                if not intentAndEntitiesDict["intent"] == basic_intent_types["unknown"]:
                    slot_val = slot_obj.slotValueExtractor(intentAndEntitiesDict)
                    if not slot_val == "" and slot_obj.slotValidation(slot_val):
                        slot_obj.slotValue = slot_val
                        self.form.fillEmptySlot(slot_obj)
                        break
                text_to_speech("Sorry! I did not understand what you just said.")
                text_to_speech(slot_obj.slotQuestion)
                user_text = speech_to_text()
                retry += 1
            slot_obj = self.form.getNextEmptySlot()

class dialogStateTracker:
    def __init__(self, form_obj):
        self.form_obj = form_obj
        self.interactionTypes = {"greet": "Hi! I am Joanna. What would you like to know about the weather?",
                                 "closure": "Alright! Bye!",
                                 "answer": ""}
        self.state = "greet"


weather_question_slots = [slot("location", "Please tell me the city name you want to know the forecast for", locationValidation, locationExtractor),
                          slot("date_time", "Please also tell me the date and time for which you would like to know the forecast", timeValidation, timeExtractor)]

