from speechToText import speech_to_text
from textToSpeech import text_to_speech
from weather_intent import load_embed, get_response
from googleweather import get_weather_info
from entity_extraction import get_location_entity


def get_user_text():
    user_text = speech_to_text()
    while len(user_text) == 0:
        user_text = speech_to_text()
    return user_text


def respond_weather_info(text):
    location = get_location_entity(text)
    weather_report = get_weather_info(location)
    text_to_speech(weather_report[0])


#respond_weather_info("What\'s the weather in Pittsburgh like?")

load_embed() # load embeddings for intent recognition
text_to_speech("Hi! I am Joanna! What can I tell you about the weather today?")
while(1):
    try:
        user_text = get_user_text()
        response_text, intent = get_response(user_text)
        text_to_speech(response_text)
        # if intent == "inform":
        #     respond_weather_info(user_text)

    except KeyboardInterrupt:
        print("press control-c again to quit")