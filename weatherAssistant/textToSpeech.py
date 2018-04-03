#!/usr/bin/env python3

import boto3
from pygame import mixer
import os
import tempfile
import time
import pyaudio
import wave
from playsound import playsound

polly = boto3.client('polly')

def play_music(wavfile):
    # define stream chunk
    chunk = 1024

    # open a wav format music
    f = wave.open(wavfile, "rb")
    # instantiate PyAudio
    p = pyaudio.PyAudio()
    # open stream
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(),
                    rate=f.getframerate(),
                    output=True)
    # read data
    data = f.readframes(chunk)

    # play stream
    while data:
        stream.write(data)
        data = f.readframes(chunk)

        # stop stream
    stream.stop_stream()
    stream.close()

    # close PyAudio
    p.terminate()

def text_to_speech(text):
    spoken_text = polly.synthesize_speech(Text=text,
                                      OutputFormat='mp3',
                                      VoiceId='Joanna')

    f = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    f.write(spoken_text['AudioStream'].read())
    f.close()
    # play_music(f.name)
    # mixer.init()
    # mixer.music.load(f.name)
    # mixer.music.play()
    # while mixer.music.get_busy() == True:
    #     pass
    # mixer.quit()
    playsound(f.name)
    while os.path.exists(f.name):
        try:
            os.remove(f.name)
            break
        except PermissionError:
            # mixer.quit()
            time.sleep(1)

# while(1):
#     text = "I am Joanna!"
#     text_to_speech(text)