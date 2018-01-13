from ChatBotFramework.dialoginfra.dataloaders import JsonDataLoader

#TODO: add logic to take args from command
def main():
    jsonLoader = JsonDataLoader("trainTuringTest.json", "JsonTuring")
    jsonLoader.load()
if __name__ == '__main__':
    main()