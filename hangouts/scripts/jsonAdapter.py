from ChatBotFramework.dialoginfra.dialogprovider import DialogProvider
from sys import argv
import json

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

def extractJsonEpisodeDetails(jsonData):
    episodeDetails = {}
    conversationKey = 'conversation'
    print(jsonData)


def JsonHangoutEpisodeLoader(logFilePath):
    with open(logFilePath) as jsonfp:
        json_data = json.load(jsonfp)
        print(json_data)

def main(args):
    # -savedLogs "C:/Users/Sumeet Singh/PycharmProjects/ChatBotFramework/ChatBotFramework/hangouts/sample_conversation.json"
    # -activeLogs "C:/Users/Sumeet Singh/PycharmProjects/ChatBotFramework/ChatBotFramework/hangouts/active_logs.json"
    savedLogFile = args['-savedLogs']
    # activeLogFile = args['-activeLogs']
    JsonHangoutEpisodeLoader(savedLogFile)

if __name__ == '__main__':
    myargs = getopts(argv)
    main(myargs)