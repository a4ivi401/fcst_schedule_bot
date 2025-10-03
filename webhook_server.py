from aiogram import Bot, Dispatcher, types
from fastapi import FastAPI, Request
import asyncio
import uvicorn
from dotenv import load_dotenv
import os

# Імпортуємо dp і bot з bot.py
from src.bot import dp, bot

load_dotenv()

# Отримуємо токен із .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Токен бота не знайдено в .env файлі")

# Перевизначаємо bot, щоб він використовував токен із .env
bot = Bot(token=BOT_TOKEN)

# Отримуємо webhook
async def handle_webhook(request: Request):
    update_json = await request.json()
    update = types.Update(**update_json)
    await dp.feed_update(bot, update)
    return {"ok": True}

app = FastAPI()
app.add_api_route("/webhook", handle_webhook, methods=["POST"])

async def start_scheduler():
    from src.parser import run_parser
    while True:
        run_parser()
        await asyncio.sleep(15 * 60)  # 15 хвилин

async def start_calendar_sync():
    from src.calendar_sync import sync_calendar_task, load_schedule_hash, get_schedule_hash
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
    # Запускаємо фонові завдання
    scheduler_task = asyncio.create_task(start_scheduler())
    calendar_task = asyncio.create_task(start_calendar_sync())

    # Запускаємо веб-сервер
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())