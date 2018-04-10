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
      "type": "service_account",
      "project_id": "speechrecognition-196601",
      "private_key_id": "1c683d9cec2c64f073b4c28e2ab38e717d7585ec",
      "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCwM+cg2fw9WkSE\nyHro0AKBHx4dM9fMXW1mMPOevHMHYJONQoSGv5Lp9AJDqv2dRawEZZ/iQWsJOiWp\nMDl5m9mWzajtopa4kelqGnTbGqFkHlTkckbhibqdN7sLKmmSOC5a//fOIsMdT6Dj\naXhwCsdZSuSZm+0uZYt/vADeERbMZj55CPOWRdV+466aE+/uhoLumjY21AGokOMt\nEXQW/JeOX9m0cI0+rPmd5H0Ezm4RjVQKbGRnNszqZyaqlFj0Z75WdlSJZdHmCWXe\nJILwQwr3wiGBS4/vwaoc96L8JXpH/NnR7jQ8fCl5+JUDgGA8MnToPiJCye6blodE\nKnhSFUXlAgMBAAECggEACGuGhzWbfeQPI6g/5VmxUPHHet5EGO47ANfkgGihd5AI\nJQcxdY34i4j/RbQJWAdhC7m+fO2i24dFjvLwwCywJmpwAOEU4j+Iv6sBfAnm/fWM\nGXmThQoTmpkz7Tnq3xOjtXIHabiUCdXJCqz61iHRumTfjS6cFCxCkQlPIk1/QSeq\nM5ml5UNJNJKZ4LJQg463c48CVYRIWcu5S1vkOowmEc0MgVJnl5kxzg/x6CCilCw6\nZhUFCErnqhEj2rsmGRRF8d2iXLy3PTRnJ3KxppEUf00RxjT0bbnmQ6WM1Qc0iSNu\nO5nvphAmg8N/Edkx5/DWt7wCxkRqVPtVUmE0pPQUuQKBgQDuijLsNBicIkxKLceD\naa0lnvVPnfIQwF3ZuWlSaztkGlac0D2AQ4ZGZoSqG6lzUGcCY48OvylSNcsFuw9B\nLOecovX7iiOs0182qeXRqjs/XuMhWeYujj6BxQS2eJwivPWOCwhEMsQd2glV01MZ\nPN9fBxM7HN2zXevYLguxgMhG7QKBgQC9GZ7fcE2txqDg6hYBpl2QNvs1zfHpizCO\nizRAx38FJlRLTysGxK/Fcczpu02rvqbgBgVG/7UJVGS2iWGW3yfD2S26LhyGO0Jc\ngItcGJUqU7srnmqKIrocQx6Y18+YYN9Ak1MgXmvqXLhZa4q1r/O9PkZt5l9G9YO/\nzlOppIHj2QKBgQDeQ0UJk80uhkLBh4B0cR4VhNScd9YaR7Pq7/k0A5iWQHhdqybz\nAXf21wVcH2Q3fz5MGoosum/9GwRt9YtUNkwlRi6fT2rIWTdJjusF/nEwLfDCnap9\nzKpvbi1i/GS3dYvz61GrggX8rrGuF7dBN9gGCmif1ti4jZX4m4bnwNBcTQKBgHr6\nd4z+XzY9cBD1i5xFEqIgb50dM09b+xcoxrG+TAgQVk+ny+aZ8WnpyYbUDf48fhBB\nOhtjXtwTa3Aexj21IQpIammjZV+SmGTKIFejkRa234nNe6IcVYbdy79A0rxZe7dm\nWHA7l9kRtb5JpyrjpBMVtf3xDVN7hdQundA8sVB5AoGAPjsU3kkFmrBzmjWfJorq\nVJhrpeR1Yyhv0fVbaU+8EBIEuXoljyoqjQsv7RQ9qOB0gi37JAGnQypbhFsEYMuY\nzvUf2an1D0a1P43ut1VI4VK51VYaXJe6A+Bh4jjF8oWbPL87BGZ3ZRS4b2JbIZ48\n7n9IrzL7LeF+YocZjIc1FEE=\n-----END PRIVATE KEY-----\n",
      "client_email": "starting-account-a11rq0svurk5@speechrecognition-196601.iam.gserviceaccount.com",
      "client_id": "106288034292686054459",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://accounts.google.com/o/oauth2/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/starting-account-a11rq0svurk5%40speechrecognition-196601.iam.gserviceaccount.com"
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
