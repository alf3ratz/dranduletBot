from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.session.aiohttp import AiohttpSession
import os


session = AiohttpSession(proxy='http://proxy.server:3128')
bot = Bot(token=os.getenv('API_TOKEN'), session=session)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Привет! Я твой новый бот. Еби меня наоборот")

@dp.message(Command("menu"))
async def show_menu(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Помощь"), KeyboardButton(text="О боте")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите действие:", reply_markup=keyboard)
@dp.message()
async def echo(message: Message):
    await message.answer_sticker("CAACAgIAAxkBAAEPFW5okmrYn2sYmaq8J7xUwj77iYv67wAC-hgAAlCx6Un0hgVIhUGOVjYE")#message.answer(f"Вы сказали: {message.text}")


# Запуск бота
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())