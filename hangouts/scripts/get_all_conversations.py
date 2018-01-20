import hangups
from boiler_plate import run_example


async def sync_recent_conversations(client, _):
    user_list, conversation_list = (
        await hangups.build_user_conversation_list(client)
    )
    all_conversations = conversation_list.get_all(include_archived=True)

    print('{} known conversations'.format(len(all_conversations)))
    for conversation in all_conversations:
        if conversation.name:
            name = conversation.name
        else:
            name = 'Unnamed conversation ({})'.format(conversation.id_)
        print('    {}'.format(name))


if __name__ == '__main__':
    run_example(sync_recent_conversations)
