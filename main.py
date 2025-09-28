import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os
from src.bot import dp, bot
from src.parser import run_parser
from src.calendar_sync import sync_calendar_task

async def start_scheduler():
    while True:
        run_parser()
        await asyncio.sleep(15 * 60)  # 15 хвилин

async def start_calendar_sync():
    while True:
        # Кожну суботу о 00:00
        now = datetime.now()
        if now.weekday() == 5 and now.hour == 0 and now.minute < 5:  # Субота, 00:00–00:04
            sync_calendar_task()
        await asyncio.sleep(60)  # Перевіряємо кожну хвилину

async def main():
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")

    if not bot_token:
        raise ValueError("Токен бота не знайдено в .env файлі")

    bot = Bot(token=bot_token)

    # Запускаємо парсер фоном
    scheduler_task = asyncio.create_task(start_scheduler())

    # Запускаємо синхронізацію календаря
    calendar_task = asyncio.create_task(start_calendar_sync())

    # Запускаємо бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())