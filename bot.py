from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Замените 'YOUR_TOKEN' на токен вашего бота
TOKEN = ''

# Хранение сообщений для поиска
messages = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я могу помогать вам искать сообщения в публичных каналах.')

async def subscribe_channel(update: Update, context: ContextTypes) -> None:
    if len(context.args) == 0:
        await update.message.reply_text('Пожалуйста, укажите имя канала.')
        return

    channel_name = context.args[0]
    try:
        # Получаем информацию о канале
        chat = await context.bot.get_chat(channel_name)
        if not chat.type in ['channel', 'supergroup']:
            await update.message.reply_text(f'{channel_name} не является каналом или супергруппой.')
            return

        # Получаем сообщения из канала
        offset = 0
        limit = 100  # Максимальное количество сообщений за один запрос
        while True:
            try:
                response = await context.bot. (chat_id=chat.id, offset=offset, limit=limit)
            except BadRequest as e:
                if str(e) == "Chat not found":
                    await update.message.reply_text(f'Канал {channel_name} не найден или бот не имеет доступа к нему.')
                    return
                raise e

            if not response.messages:
                break
            for message in response.messages:
                if message.text:
                    messages[message.message_id] = (message.text, message.chat_id)
            offset += limit

        await update.message.reply_text(f'Подписка на канал {channel_name} завершена.')
    except Exception as e:
        await update.message.reply_text(f'Не удалось подписаться на канал {channel_name}: {str(e)}')

async def search_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_text('Пожалуйста, укажите текст для поиска.')
        return

    query = ' '.join(context.args)
    results = [msg_id for msg_id, (text, chat_id) in messages.items() if query.lower() in text.lower()]

    if results:
        response = f'Найдено {len(results)} сообщений:\n'
        for msg_id in results:
            response += f'https://t.me/c/{abs(messages[msg_id][1])}/{msg_id}\n'
        await update.message.reply_text(response)
    else:
        await update.message.reply_text('Сообщений не найдено.')

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe_channel))
    application.add_handler(CommandHandler("search", search_message))

    application.run_polling()

if __name__ == '__main__':
    main()