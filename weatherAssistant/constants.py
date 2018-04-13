WEATHER_TERMS = ["weather", "climate", "precipitation", "sun", "rain", "cloud", "snow", "hot", "humid", "cold",
                "sunny", "windy", "cloudy", "rainy", "snowy", "misty", "foggy", "colder", "hotter", "warmer", "pleasant"]
GREET_TERMS = ["hello", "hey", "howdy", "hello", "hi", "yo", "yaw"]
CLOSURE_TERMS = ["thank you", "bye", "tata", "thanks", "that will be all", "that's it", "that'll be all"]

DAY_TERMS = {"dawn":"5:00", "dusk":"17:00", "morning":"8:00", "evening":"19:00", "noon":"12:00", "afternoon":"14:00", "night": "22:00", "tonight":"22:00", "midnight":"00:00", "midday":"12:00"}
TIME_ABRV = {"MO":"morning", "AF":"afternoon","EV":"evening" ,"NI":"night"}
DATE_TERMS = {"today":0, "tomorrow":1}
DAY_OF_WEEK = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, "Friday":4, "Saturday":5,"Sunday":6}

YES_TERMS = ["yes", "yup", "uh-huh", "correct", "right", "true"]
NO_TERMS = ["no", "nope", "nada","false", "not"]

from enum import Enum

class DIALOG_STATES(Enum):
    GREET = 0
    ASK = 1
    FILL = 2
    CONF_CANCEL = 3
    REPORT = 4
    CLOSURE = 5
    HELP = 6

class INTENT_TYPES(Enum):
    GRT = 0
    WTH_QU = 1
    ANS_YES = 2
    ANS_NO = 3
    ANS_SLT = 4
    UNK = 5
    CLS = 6
    CANCL = 7
    HLP = 8
    RPT = 9
