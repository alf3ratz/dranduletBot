import os
import re
import argparse
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import FloodWaitError, InviteHashExpiredError, InviteRequestSentError
from telethon.tl.functions.messages import ImportChatInviteRequest

# Подсказка: можно положить ключи в переменные окружения TELEGRAM_API_ID и TELEGRAM_API_HASH
def get_api_credentials():
    api_id = ""#os.getenv("TELEGRAM_API_ID")
    api_hash = ""#os.getenv("TELEGRAM_API_HASH")
    if not api_id:
        api_id = input("Введите api_id: ").strip()
    if not api_hash:
        api_hash = input("Введите api_hash: ").strip()
    return int(api_id), api_hash

async def resolve_entity_and_join_if_needed(client: TelegramClient, group_str: str):
    s = group_str.strip()

    # Если это приватная инвайт-ссылка формата t.me/+HASH или t.me/joinchat/HASH
    m = re.search(r't\.me/(?:\+|joinchat/)([A-Za-z0-9_-]+)', s)
    if m:
        invite_hash = m.group(1)
        try:
            updates = await client(ImportChatInviteRequest(invite_hash))
            chat = updates.chats[0]
            entity = await client.get_entity(chat)
            return entity
        except (InviteHashExpiredError, InviteRequestSentError) as e:
            raise RuntimeError(f"Не удалось вступить по инвайт-ссылке: {e}")
        except Exception as e:
            raise RuntimeError(f"Ошибка при попытке вступить по инвайту: {e}")

    # Иначе это публичный юзернейм/ссылка вида t.me/username или @username или просто username
    if s.startswith("http"):
        s = s.rstrip("/").split("/")[-1]
    if s.startswith("@"):
        s = s[1:]

    # Для публичных каналов/групп достаточно получить entity
    try:
        entity = await client.get_entity(s)
        return entity
    except Exception as e:
        raise RuntimeError(f"Не удалось получить группу/канал '{group_str}': {e}")

def parse_date(date_str: str | None):
    if not date_str:
        return None
    # Поддержка простого формата YYYY-MM-DD
    return datetime.strptime(date_str, "%Y-%m-%d")

async def fetch_messages(group: str, limit: int, since: str | None, print_sender: bool):
    api_id, api_hash = get_api_credentials()
    # Сессия сохранится в файле session_get_messages.session
    async with TelegramClient("session_get_messages", api_id, api_hash) as client:
        # При первом запуске спросит телефон/код/пароль (если нужен)
        await client.start()

        entity = await resolve_entity_and_join_if_needed(client, group)
        offset_date = parse_date(since)

        # reverse=True чтобы печатать в хронологическом порядке (старые -> новые)
        count = 0
        async for msg in client.iter_messages(entity, limit=limit, offset_date=offset_date, reverse=True):
            # Пропускаем сервисные сообщения (вступил/вышел и т.п.), если нужно
            if msg.message is None and not msg.media:
                continue

            if print_sender:
                try:
                    sender = await msg.get_sender()
                    sender_name = None
                    if sender:
                        sender_name = getattr(sender, "username", None) or \
                                      (f"{getattr(sender, 'first_name', '')} {getattr(sender, 'last_name', '')}".strip()) or \
                                      str(sender.id)
                    else:
                        sender_name = "Unknown"
                except Exception:
                    sender_name = "Unknown"
            else:
                sender_name = ""

            text = msg.message or ""
            text = text.replace("\n", " ").replace("\r", " ")

            if print_sender:
                print(f"{msg.id}\t{msg.date.isoformat()}\t{sender_name}\t{text}")
            else:
                print(f"{msg.id}\t{msg.date.isoformat()}\t{text}")

            count += 1

        if count == 0:
            print("Сообщения не найдены (возможно, у вас нет доступа или неверные параметры).")

def main():
    parser = argparse.ArgumentParser(description="Получение сообщений из группы/канала Telegram (Telethon).")
    parser.add_argument("--group", required=True, help="Ссылка t.me/..., @username или username группы/канала")
    parser.add_argument("--limit", type=int, default=100, help="Сколько сообщений получить (по умолчанию 100)")
    parser.add_argument("--since", default=None, help="Начать с даты (YYYY-MM-DD), например 2024-01-01")
    parser.add_argument("--nosender", action="store_true", help="Не выводить отправителя")
    args = parser.parse_args()

    try:
        asyncio.run(fetch_messages(args.group, args.limit, args.since, print_sender=not args.nosender))
    except FloodWaitError as e:
        print(f"Слишком много запросов, подождите {e.seconds} секунд.")
    except KeyboardInterrupt:
        print("Остановлено пользователем.")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()