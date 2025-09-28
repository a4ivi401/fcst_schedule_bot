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
    from src.calendar_sync import load_schedule_hash, get_schedule_hash
    from src.parser import load_schedule_cache

    while True:
        # Перевіряємо, чи змінився розклад
        schedule = load_schedule_cache()
        if not schedule:
            await asyncio.sleep(15 * 60)  # Зачекати 15 хв, якщо немає розкладу
            continue

        current_hash = get_schedule_hash(schedule)
        previous_hash = load_schedule_hash()

        if current_hash != previous_hash:
            print("🔄 Виявлено зміни в розкладі. Запускаємо синхронізацію календаря...")
            sync_calendar_task()

        await asyncio.sleep(15 * 60)  # Перевіряємо кожні 15 хвилин

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