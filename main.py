import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os
from src.bot import dp, bot
from src.parser import run_parser

async def start_scheduler():
    while True:
        run_parser()
        await asyncio.sleep(15 * 60)  # 15 хвилин

async def main():
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")

    if not bot_token:
        raise ValueError("Токен бота не знайдено в .env файлі")

    bot = Bot(token=bot_token)

    # Запускаємо парсер фоном
    scheduler_task = asyncio.create_task(start_scheduler())

    # Запускаємо бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())