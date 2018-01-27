from ChatBotFramework.dialoginfra.dialogprovider import DialogProvider
from ChatBotFramework.dialoginfra.episodeformats import JsonBasicEpisode
import json
from sys import argv
import random
import time
#TODO: add logic to take args from command

def getopts(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] == '-':  # Found a "-name value" pair.
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
            if len(argv) >= 2:
                argv = argv[2:]  # Reduce the argument list by copying it starting from index 1.
        else:
            argv = argv[1:]
    return opts

def main(args):
    # -userId bob -savedLogs "C:/Users/Sumeet Singh/PycharmProjects/ChatBotFramework/ChatBotFramework/test/sampledialogfile.json" -activeLogs "C:/Users/Sumeet Singh/PycharmProjects/ChatBotFramework/ChatBotFramework/test/saveddialogfile.json"
    userId = args['-userId']
    savedLogFile = args['-savedLogs']
    activeLogFile = args['-activeLogs']
    dialogProvider = DialogProvider(platformId = "CLI", sessionId = 9999, activeLogFilePath = activeLogFile)
    dialogProvider.InitializeDialogProvider(savedLogFile)
    turn = 0
    prevResponseIndex = -1
    botResponses = ["How are you?", "How should I know? I am dumb!", "I am sad :(", "I am happy :)"]
    while True:
        timestamp = time.time()
        newUtterance ={'userId':"", 'text':"", "timestamp": timestamp}
        if turn%2 > 0:
            utteranceText = input(userId + ": ")
            newUtterance['userId'] = userId
            newUtterance['text'] = utteranceText
        else:
            reply_text = "Hi I am Alice! How may I assit you?"
            if turn > 0:
                indices = list(range(0, len(botResponses)))
                if prevResponseIndex != -1:
                    indices.remove(prevResponseIndex)
                random_index = random.choice(indices)
                reply_text = botResponses[random_index]
                prevResponseIndex = random_index
            print("Alice: "+reply_text)
            newUtterance['userId'] = 'Alice'
            newUtterance['text'] = reply_text
        turn += 1
        dialogProvider.UpdateJson(utterance = newUtterance)
        if 'exit' in newUtterance['text']:
            break
    dialogProvider.PersistJson()
    #print(json.dumps(dialogProvider.episodes, cls= CustomEncoder))

if __name__ == '__main__':
    myargs = getopts(argv)
    main(myargs)