import asyncio
from telethon import TelegramClient, events, errors

# Замените на ваши данные
api_id = ''
api_hash = ''
bot_token = '-'
phone_number = ''  # Номер телефона, зарегистрированный в Telegram
# Создание клиента Telethon
client = TelegramClient('session_name', api_id, api_hash)

# Хранение сообщений для поиска
messages = {}

async def main():
    await client.start(phone=phone_number)

    # Подписка на канал
    await subscribe_channel('@Cbpub')

    # Поиск сообщений
    await search_message('текст для поиска')

    await client.disconnect()

async def subscribe_channel(channel_name):
    try:
        # Получаем информацию о канале
        chat = await client.get_entity(channel_name)
        if not chat.megagroup and not chat.broadcast:
            print(f'{channel_name} не является каналом или супергруппой.')
            return

        # Получаем сообщения из канала
        async for message in client.iter_messages(chat):
            if message.text:
                messages[message.id] = (message.text, message.chat_id)

        print(f'Подписка на канал {channel_name} завершена.')
    except errors.ChannelInvalidError:
        print(f'Канал {channel_name} не найден или пользователь не имеет доступа к нему.')
    except ValueError as ve:
        print(f'Не удалось найти канал {channel_name}: {str(ve)}')
    except Exception as e:
        print(f'Не удалось подписаться на канал {channel_name}: {str(e)}')

async def search_message(query):
    results = [msg_id for msg_id, (text, chat_id) in messages.items() if query.lower() in text.lower()]

    if results:
        response = f'Найдено {len(results)} сообщений:\n'
        for msg_id in results:
            response += f'https://t.me/c/{abs(messages[msg_id][1])}/{msg_id}\n'
        print(response)
    else:
        print('Сообщений не найдено.')

if __name__ == '__main__':
    asyncio.run(main())