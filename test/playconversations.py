from ChatBotFramework.dialoginfra.dialogprovider import DialogProvider
from ChatBotFramework.dialoginfra.episodeformats import JsonBasicEpisode
import json
#TODO: add logic to take args from command


def main():
    dialogProvider = DialogProvider(platformId = "testing", sessionId = 9999, activeLogFilePath = "C:/Users/Sumeet Singh/PycharmProjects/ChatBotFramework/ChatBotFramework/test/saveddialogfile.json")
    dialogProvider.InitializeDialogProvider("C:/Users/Sumeet Singh/PycharmProjects/ChatBotFramework/ChatBotFramework/test/sampledialogfile.json")
    newUtterance = {'userId':'bot', 'text': 'How may I assist you'}
    dialogProvider.UpdateJson(utterance = newUtterance)
    dialogProvider.PersistJson()
    #print(json.dumps(dialogProvider.episodes, cls= CustomEncoder))

if __name__ == '__main__':
    main()