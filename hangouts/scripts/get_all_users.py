import hangups

from boiler_plate import run_example


async def sync_recent_conversations(client, _):
    user_list, conversation_list = (
        await hangups.build_user_conversation_list(client)
    )
    all_users = user_list.get_all()

    print('{} known users'.format(len(all_users)))
    for user in all_users:
        print('    {}: {}'.format(user.full_name, user.id_.gaia_id))



if __name__ == '__main__':
    run_example(sync_recent_conversations)
