"""
This file defines the control mechanism to rank the slots
"""
from speechToText import speech_to_text
from textToSpeech import text_to_speech
from ner_extractor import NLUModule
from constants import WEATHER_TERMS, GREET_TERMS, DATE_TERMS, CLOSURE_TERMS, DAY_TERMS, DAY_OF_WEEK, INTENT_TYPES, DIALOG_STATES
from datetime import datetime, date, time,timedelta
from weather_report import weather_report
import random
import copy

MACHINE_CONTROL = False

def timeExtractor(intentAndEntityDict):
    dateVal = intentAndEntityDict["entities"]["DATE"]
    timeVal = intentAndEntityDict["entities"]["TIME"]
    dateToday = datetime.today()
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

    queryDate = dateToday + timedelta(days=addDays)
    if not hours == -1:
        queryDate = datetime(queryDate.year, queryDate.month, queryDate.day, hours)
    return queryDate

class slot:
    def __init__(self, slotName, slotQuestion):
        self.slotName = slotName
        self.slotValue = ""
        self.slotQuestion = slotQuestion

    def isValid(self):
        return NotImplementedError

class dateSlot(slot):
    def __init__(self,slotName=None, slotQuestion=None):
        slotName = "DATE"
        slotQuestion = "Could you please give me a date or time?"
        super().__init__(slotName, slotQuestion)

    def isValid(self):
        # TODO: check that self.slotValue is a valid date-time
        return True

class timeSlot(slot):
    def __init__(self,slotName=None, slotQuestion=None):
        slotName = "TIME"
        slotQuestion = "Could you please give me a date or time?"
        super().__init__(slotName, slotQuestion)

    def isValid(self):
        # TODO: check that self.slotValue is a valid date-time
        return True

class locationSlot(slot):
    def __init__(self, slotName=None, slotQuestion=None):
        slotName = "LOCATION"
        slotQuestion = "Could you please give me a city name?"
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

    def isFilled(self):
        return self.getNextEmptySlot() is None

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

    def emptyFilledSlot(self, slot_obj):
        for i in range(len(self.filledSlots)):
            if self.filledSlots[i].slotName == slot_obj.slotName:
                self.emptySlots.append(slot_obj)
                del self.filledSlots[i]
                break

    def clearForm(self):
        allSlots = self.emptySlots + self.filledSlots
        self.emptySlots = allSlots
        self.filledSlots = []

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
        self.visited = False
        self.revisitMsg = ["What else can I tell you today?"]

    def run(self, input=None):
        if not self.visited:
            text_to_speech(random.choice(self.greetings))
            self.visited = True
        else:
            text_to_speech(random.choice(self.revisitMsg))

class ask(dialState):
    def __init__(self, name, nluModule, form_obj):
        super().__init__(name, nluModule)
        self.form = form_obj

    def run(self, input=None):
        slotResponse = ""
        empty_slot_obj = self.form.getNextEmptySlot()
        text_to_speech(empty_slot_obj.slotQuestion)
        user_text = speech_to_text()
        slotResponse = user_text
        if len(slotResponse) > 0:
            global MACHINE_CONTROL
            MACHINE_CONTROL = True
        return slotResponse

# Class for building context by filling the form within a dialog systems
class fill(dialState):
    def __init__(self, name, nluModule, form_obj):
        super().__init__(name, nluModule)
        self.form = form_obj

    # input is a dict with key containing slotName
    def run(self, input):
        errorMessages = []

        for key in input.keys():
            slotToFill = self.form.getSlotByName(key)
            if not input[key] == "" and not slotToFill is None:
                tempSlot = copy.deepcopy(slotToFill)
                tempSlot.slotValue = input[key]
                try:
                    if not tempSlot.isValid():
                        errMsg = "Slot {}. Incorrect Value {}".format(tempSlot.slotName,tempSlot.slotValue)
                        errorMessages.append(errMsg)
                        print(errMsg)
                        self.form.emptyFilledSlot(slotToFill)
                        continue
                except NotImplementedError:
                    print("\n Slot {} not initialized", slotToFill.slotName)
                if not slotToFill.slotValue == "":
                    print("\n Overwriting slot {} having value {}".format(slotToFill.slotName,slotToFill.slotValue))
                slotToFill.slotValue = input[key]
                self.form.fillEmptySlot(slotToFill)

        if len(errorMessages) > 0:
            text_to_speech("Sorry, Invalid value was provided for the following slots.")
            for errMsg in errorMessages:
                text_to_speech(errMsg)

        global MACHINE_CONTROL
        MACHINE_CONTROL = True

        return None

class report(dialState):
    def __init__(self, name, nluModule,weather_form, weather_reporter):
        super().__init__(name, nluModule)
        self.weather_form = weather_form
        self.weather_reporter = weather_reporter

    # constructs and reads out the full weather report
    # input is ignored. The weather form is iterated through and used.
    def run(self, input):
        # after report generation is done we want to automatically go back to greet state
        # without processing any input. Hence, setting MACHINE_CONTROL
        global MACHINE_CONTROL
        MACHINE_CONTROL = True
        # TODO: this is an abuse
        # We should have instead iterated through the form's slots
        location = 'Washington'
        dt_tm_obj = datetime.now()
        dt_tm_obj.replace(hour=dt_tm_obj.hour+1) #get weather for the next hour
        inputTime = None

        for slot in self.weather_form.filledSlots:
            if slot.slotName == 'LOCATION':
                location = slot.slotValue
            elif slot.slotName == 'DATE':
                inputDate = datetime.strptime(slot.slotValue, '%Y-%m-%d')
                dt_tm_obj = dt_tm_obj.replace(year=inputDate.year, month=inputDate.month, day=inputDate.day)
            elif slot.slotName == 'TIME':
                inputTime = datetime.strptime(slot.slotValue, '%H:%M')
                dt_tm_obj = dt_tm_obj.replace(hour=inputTime.hour, minute=inputTime.minute)

        text_to_speech("The weather in {} ".format(location))
        dayRep, hrRep = self.weather_reporter.get_weather_report(location, dt_tm_obj)
        text_to_speech(dayRep)
        # Generate hour report only if the user provides time
        if not inputTime is None:
            text_to_speech(hrRep)

        return None

class closure(dialState):
    def __init__(self, name, nluModule):
        super().__init__(name, nluModule)
        self.closureMsg = ["It was a pleasure assisting you. Speak to you soon!"]

    def run(self, input=None):
        text_to_speech(random.choice(self.closureMsg))
        return None

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
    def __init__(self,  startState, stopState, nluModule, stateTable, stateDict, dialogForm):
        self.start = startState
        self.stop = stopState
        self.currentState = startState
        self.nlu = nluModule
        self.stateTable = stateTable
        self.stateDict = stateDict
        self.dialogForm = dialogForm

    def reset(self):
        self.currentState = self.start
        self.dialogForm.clearForm()

    def run(self):
        output = None
        stateDict[self.currentState.value].run()
        while not self.currentState.value is self.stop.value:
            try:
                global MACHINE_CONTROL
                user_input = None
                input = None

                if MACHINE_CONTROL:
                    if self.currentState == DIALOG_STATES.FILL:
                        if self.dialogForm.isFilled():
                            self.currentState = DIALOG_STATES.REPORT
                        else:#incorrect slot filled or some slot empty
                            # go to ask state and in it's run we'll get a response
                            self.currentState = DIALOG_STATES.ASK
                    elif self.currentState == DIALOG_STATES.ASK:
                        #process the output from previous run of ask state
                        user_input = output
                    elif self.currentState == DIALOG_STATES.REPORT:
                        self.currentState = DIALOG_STATES.GREET

                    MACHINE_CONTROL = False
                else:
                    user_input = speech_to_text()
                    while user_input == "":
                        text_to_speech("Sorry! I did not catch that. Would you like to try again?")
                        user_input = speech_to_text()

                # analyze user input for intent and entities in the current or previous solicitation
                if not user_input is None:
                    try:
                        intentAndEntitiesDict = self.nlu.DiscoverIntentAndEntities(user_input)
                        intentType = intentAndEntitiesDict["intent"]
                        self.currentState = self.stateTable[self.currentState.value][intentType.value]
                        input = intentAndEntitiesDict["entities"]
                    except:
                        text_to_speech("Uh Oh! I think there was something wrong with me. Got to go!")

                output = None
                output = self.stateDict[self.currentState.value].run(input)

            except:
                raise Exception("Failure during state transition from state:{}".format(self.currentState))

def CreateWeatherForm():
    slots = [dateSlot(), timeSlot(), locationSlot()]
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
    weather_reporter = weather_report()
    reportWeather = report("report", None, weather_form,weather_reporter)
    closeState = closure("closure", None)
    helpState = None

    stateDict = {DIALOG_STATES.GREET: greetState,
                 DIALOG_STATES.ASK: askState,
                 DIALOG_STATES.FILL: fillState,
                 DIALOG_STATES.CONF_CANCEL:confCancel,
                 DIALOG_STATES.REPORT:reportWeather,
                 DIALOG_STATES.CLOSURE: closeState,
                 DIALOG_STATES.HELP :helpState}
    return stateDict,weather_form

def InitializeStateTable():
    stateTable = [[None for y in range(len(list(INTENT_TYPES)))] for x in range(len(list(DIALOG_STATES)))]

    stateTable[DIALOG_STATES.GREET.value][INTENT_TYPES.GRT.value] = DIALOG_STATES.GREET
    stateTable[DIALOG_STATES.GREET.value][INTENT_TYPES.WTH_QU.value] = DIALOG_STATES.ASK
    stateTable[DIALOG_STATES.GREET.value][INTENT_TYPES.ANS_SLT.value] = DIALOG_STATES.FILL
    stateTable[DIALOG_STATES.GREET.value][INTENT_TYPES.CLS.value] = DIALOG_STATES.CLOSURE
    stateTable[DIALOG_STATES.GREET.value][INTENT_TYPES.ANS_YES.value] = DIALOG_STATES.ASK
    stateTable[DIALOG_STATES.GREET.value][INTENT_TYPES.ANS_NO.value] = DIALOG_STATES.CLOSURE
    stateTable[DIALOG_STATES.GREET.value][INTENT_TYPES.UNK.value] = DIALOG_STATES.GREET

    stateTable[DIALOG_STATES.ASK.value][INTENT_TYPES.WTH_QU.value] = DIALOG_STATES.ASK
    stateTable[DIALOG_STATES.ASK.value][INTENT_TYPES.ANS_SLT.value] = DIALOG_STATES.FILL
    stateTable[DIALOG_STATES.ASK.value][INTENT_TYPES.CLS.value] = DIALOG_STATES.CLOSURE
    stateTable[DIALOG_STATES.ASK.value][INTENT_TYPES.ANS_NO.value] = DIALOG_STATES.CLOSURE
    stateTable[DIALOG_STATES.ASK.value][INTENT_TYPES.ANS_YES.value] = DIALOG_STATES.ASK

    return stateTable

if __name__ == "__main__":
    nlu = NLUModule()
    stateDict,weather_form = InitializeDialogStates()
    stateTrans= InitializeStateTable()

    weather_dialog = dialogProcessor(startState=DIALOG_STATES.GREET,
                                     stopState=DIALOG_STATES.CLOSURE,
                                     nluModule=nlu,
                                     stateTable=stateTrans,
                                     stateDict=stateDict,
                                     dialogForm= weather_form)
    while 1:
        weather_dialog.run()
        response = input("Press Y/y to continue. Any other key to exit :")
        if not (response == "Y" or response == "y"):
            break
        weather_dialog.reset()