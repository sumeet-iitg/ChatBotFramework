import speech_recognition as sr
import tempfile
import pyaudio
import wave

AUDIO_FILE = ("C:/Users/Sumeet Singh/Documents/Lectures/11-754 DialogueSystems/wav files/weather_hyderabad.wav")

# use the audio file as the audio source
def get_recording():
    f = tempfile.NamedTemporaryFile(prefix="weather_", suffix=".wav", delete=False)
    f.close()

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = f.name

    audio = pyaudio.PyAudio()

    # start Recording
    print("\n Recording...")
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("\nfinished recording")

    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    return WAVE_OUTPUT_FILENAME

# TODO: Fix exception in saveAudioFile
def saveAudioFile(wavData):
    f = tempfile.NamedTemporaryFile(prefix="weather_", suffix=".wav", delete=False)
    f.close()

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    WAVE_OUTPUT_FILENAME = f.name
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(wavData.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(wavData)
    waveFile.close()

GOOGLE_CLOUD_SPEECH_CREDENTIALS = r"""{
         }"""

def speech_to_text():
    r = sr.Recognizer()
    # with sr.WavFile(AUDIO_FILE) as source:              # use "test.wav" as the audio source
    #     audio = r.record(source)                        # extract audio data from the file

    # with sr.WavFile(get_recording()) as source:
    #     audio = r.record(source)

    # for index, name in enumerate(sr.Microphone.list_microphone_names()):
    #     print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))
    recognized_text = ""
    with sr.Microphone(device_index=0) as source:
        print("Say something!")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        recognized_text = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
        print("Google Cloud Speech thinks you said: \" " + recognized_text + "\"")
    except sr.UnknownValueError:
        print("Google Cloud Speech could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Cloud Speech service; {0}".format(e))
    return recognized_text

speech_to_text()

# import os
# from pocketsphinx import LiveSpeech, get_model_path
#
# model_path = get_model_path()
#
# speech = LiveSpeech(
#     verbose=False,
#     sampling_rate=16000,
#     buffer_size=2048,
#     no_search=False,
#     full_utt=False,
#     hmm=os.path.join(model_path, 'en-us'),
#     lm=os.path.join(model_path, 'en-us.lm.bin'),
#     dic=os.path.join(model_path, 'cmudict-en-us.dict')
# )
#
# for phrase in speech:
#     print(phrase)

# import os
# from pocketsphinx import AudioFile, get_model_path, get_data_path
#
# model_path = get_model_path()
# data_path = get_data_path()
#
# config = {
#     'verbose': False,
#     'audio_file': "C:/Users/Sumeet Singh/Documents/Lectures/11-754 DialogueSystems/wav files/hello.wav" ,
#     'buffer_size': 2048,
#     'no_search': False,
#     'full_utt': False,
#     'hmm': os.path.join(model_path, 'en-us'),
#     'lm': os.path.join(model_path, 'en-us.lm.bin'),
#     'dict': os.path.join(model_path, 'cmudict-en-us.dict')
# }
#
# audio = AudioFile(**config)
# for phrase in audio:
#     print(phrase)
