"""
This file defines the control mechanism to rank the slots
"""
from speechToText import speech_to_text
from textToSpeech import text_to_speech
from ner_extractor import NLUModule, basic_intent_types
from constants import WEATHER_TERMS, GREET_TERMS, DATE_TERMS, CLOSURE_TERMS, DAY_TERMS, DAY_OF_WEEK, INTENT_TYPES, DIALOG_STATES
import datetime
import random
import copy

def timeExtractor(intentAndEntityDict):
    dateVal = intentAndEntityDict["entities"]["DATE"]
    timeVal = intentAndEntityDict["entities"]["TIME"]
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

class slot:
    def __init__(self, slotName, slotQuestion):
        self.slotName = slotName
        self.slotValue = ""
        self.slotQuestion = slotQuestion

    def isValid(self):
        return NotImplementedError

class timeSlot(slot):
    def __init__(self,slotName=None, slotQuestion=None):
        slotName = "timeSlot"
        slotQuestion = "Could you please tell me the date and time for which you would like to know the forecast?"
        super().__init__(slotName, slotQuestion)

    def isValid(self):
        # TODO: check that self.slotValue is a valid date-time
        return True

class locationSlot(slot):
    def __init__(self, slotName=None, slotQuestion=None):
        slotName = "locationSlot"
        slotQuestion = "Please tell me the city name you want to know the forecast for?"
        super().__init__(slotName, slotQuestion)

    def isValid(self):
        # TODO: check that self.slotValue is a valid location
        return True

# Class to represent a form in dialog systems
# A form has slot names and associated questions
# For each empty slot, the system asks the necessary question
class form:
    def __init__(self, slots):
        self.emptySlots = slots
        self.filledSlots = []

    def getSlotByName(self, slotName):
        allSlots = self.emptySlots + self.filledSlots
        for slot in allSlots:
            if slot.slotName == slotName:
                return slot
        return None

    def getNextEmptySlot(self):
        slot_obj = None
        if len(self.emptySlots) > 0:
            slot_obj = self.emptySlots[0]
        return slot_obj

    def fillEmptySlot(self, slot_obj):
        for i in range(len(self.emptySlots)):
            if self.emptySlots[i].slotName == slot_obj.slotName:
                self.filledSlots.append(slot_obj)
                del self.emptySlots[i]
                break

class dialState:
    def __init__(self, name, nluModule):
        self.name = name
        self.nluModule = nluModule

    def run(self, input):
        return NotImplementedError

class greet(dialState):
    def __init__(self,name, nluModule):
        super().__init__(name,nluModule)
        self.greetings = ["Hello! How may I help you with the weather?",
                          "Hi! What would you like to know about the weather?"]

    def run(self, input=None):
        text_to_speech(random.choice(self.greetings))

class ask(dialState):
    def __init__(self, name, nluModule, form_obj):
        super().__init__(name, nluModule)
        self.form = form_obj

    def run(self, input=None):
        slotResponse = {}
        for slot_obj in self.form.emptySlots:
            text_to_speech(slot_obj.slotQuestion)
            user_text = speech_to_text()
            slotResponse[slot_obj.slotName] = user_text
        return slotResponse

# Class for building context by filling the form within a dialog systems
class fill(dialState):
    def __init__(self, name, nluModule, form_obj):
        super().__init__(name, nluModule)
        self.form = form_obj

    # input is a dict with key containing slotName
    def run(self, input):
        incorrectSlots = []
        for key in input.keys():
            slotToFill = self.form.getSlotByName(key)
            if not input[key] == "" and not slotToFill is None:
                tempSlot = copy.deepcopy(slotToFill)
                tempSlot.slotValue = input[key]
                try:
                    if not tempSlot.isValid():
                        print("\n Invalid value provided for Slot{}, Value:{}".format(tempSlot.slotName,tempSlot.slotValue))
                        incorrectSlots.append(tempSlot)
                        continue
                except NotImplementedError:
                    print("\n Slot {} not initialized", slotToFill.slotName)
                if not slotToFill.slotValue == "":
                    print("\n Overwriting slot {} having value {}".format(slotToFill.slotName,slotToFill.slotValue))
                slotToFill.slotValue = input[key]
                self.form.fillEmptySlot(slotToFill)

        return incorrectSlots

class report(dialState):
    def __init__(self, name, nluModule):
        super().__init__(name, nluModule)

    # constructs and reads out the full weather report
    # input is dict of LOCATION, DATE and DURATION
    def run(self, input):
        return NotImplementedError

class closure(dialState):
    def __init__(self, name, nluModule):
        super().__init__(name, nluModule)

    def run(self, input):
        return NotImplementedError

class confirm(dialState):
    def __init__(self, name, nluModule):
        super().__init__(name, nluModule)

    def run(self, input):
        return NotImplementedError

class help(dialState):
    def __init__(self, name, nluModule):
        super().__init__(name, nluModule)
        self.transitionFunc = self.transition

    def transition(self, input):
        if type(input) is str:
            pass
        elif type(input) is dict:
            pass

class repeat(dialState):
    def __init__(self, name, nluModule):
        super().__init__(name, nluModule)
        self.transitionFunc = self.transition

    def transition(self, input):
        if type(input) is str:
            pass
        elif type(input) is dict:
            pass

class dialogProcessor:
    def __init__(self,  startState, stopState, nluModule, stateTable, stateDict):
        self.start = self.startState
        self.stop = self.stopState
        self.currentState = None
        self.nlu = nluModule
        self.stateTable = stateTable
        self.stateDict = stateDict

    def start(self, input=None):
        while not self.currentState is self.stop:
            try:
                intentAndEntitiesDict = self.nluModule.DiscoverIntentAndEntities(user_text)
                self.currentState, input = self.currentState.run(intentAndEntitiesDict)
                retry = 0
                while retry < self.retryCount:
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
                continue
            except:
                raise Exception("Failure during state transition from state:%s", self.currentState.name)

def CreateWeatherForm():
    slots = [timeSlot(), locationSlot()]
    weather_form = form(slots)
    return weather_form

'''
------------|
Input types | 
\\\\\\\\\\\\|
States      | "grt"     "wth_qu" "ans_yes" "ans_No" "ans_slot" "unk" "close" "cancl"  "hlp"  "rpt" 
------------|
0:greet         0        1       0          0       NA         NA      4     NA          5       0
1:ask           NA       1       1          2       1          NA      2     2           1       1 
2:conf_cancl    NA       1       1          1       NA         NA      4     0           2       2     
3:report(Temp)  NA       1       1          1       1          NA      4     NA          1       3             
4:closure       NA       NA      NA         NA      NA         NA      NA    NA          NA      NA
5:help          0        1       0          0       0          5       4     0           5       5 
'''
def InitializeDialogStates():
    greetState = greet("greet",None)

    weather_form = CreateWeatherForm()
    askState = ask("ask", None, weather_form)
    fillState = fill("fill", None,weather_form)
    confCancel = None
    reportWeather = report("report", None)
    closeState = closure("closure", None)
    helpState = None

    stateDict = {DIALOG_STATES.GREET: greetState,
                 DIALOG_STATES.ASK: askState,
                 DIALOG_STATES.FILL: fillState
                 DIALOG_STATES.CONF_CANCEL:confCancel,
                 DIALOG_STATES.REPORT:reportWeather,
                 DIALOG_STATES.CLOSURE: closeState,
                 DIALOG_STATES.HELP :helpState}
    return stateDict

def InitializeStateTable():
    stateTable = [[None for y in range(len(list(INTENT_TYPES)))] for x in range(len(list(DIALOG_STATES)))]

    stateTable[DIALOG_STATES.GREET][INTENT_TYPES.GRT] = DIALOG_STATES.GREET
    stateTable[DIALOG_STATES.GREET][INTENT_TYPES.WTH_QU] = DIALOG_STATES.ASK
    stateTable[DIALOG_STATES.GREET][INTENT_TYPES.CLOSE] = DIALOG_STATES.CLOSURE

    stateTable[DIALOG_STATES.ASK][INTENT_TYPES.WTH_QU] = DIALOG_STATES.FILL
    stateTable[DIALOG_STATES.ASK][INTENT_TYPES.ANS_SLT] = DIALOG_STATES.FILL
    stateTable[DIALOG_STATES.ASK][INTENT_TYPES.CLOSE] = DIALOG_STATES.CLOSURE

    return stateTable


if __name__ == "__main__":
    nlu = NLUModule()
    stateDict = InitializeDialogStates()
    stateTrans= InitializeStateTable()

    weather_dialog = dialogProcessor(startState=stateDict[DIALOG_STATES.GREET],
                                     stopState=stateDict[DIALOG_STATES.CLOSURE],
                                     nluModule=nlu,
                                     stateTable=stateTrans,
                                     stateDict=stateDict)
    while 1:
        weather_dialog.start()
        response = input("Press Y/y to continue. Any other key to exit :")
        if not (response == "Y" or response == "y"):
            break


