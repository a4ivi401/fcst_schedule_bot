from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from dotenv import load_dotenv
import os
import json

# Завантажуємо змінні з .env
load_dotenv()

# Отримуємо токен з .env
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Токен бота не знайдено в .env файлі")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def load_schedule_cache():
    path = 'data/schedule_cache.json'
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Привіт! Я бот для перегляду розкладу. Використовуй:\n /today для перегляду розкладу на сьогодні \n /week для перегляду розкладу на тиждень")

@dp.message(Command("today"))
async def cmd_today(message: types.Message):
    schedule = load_schedule_cache()

    if not schedule:
        await message.answer("Розклад не знайдено. Спробуй пізніше.")
        return

    from datetime import datetime
    today_name = {
        0: "Понеділок",
        1: "Вівторок",
        2: "Середа",
        3: "Четвер",
        4: "П'ятниця",
        5: "Субота",
        6: "Неділя"
    }[datetime.now().weekday()]

    lessons = schedule.get(today_name, [])
    if not lessons:
        await message.answer(f"🥳 Сьогодні ({today_name}) пар немає.")
        return

    response = f"📅 Розклад на <b>{today_name}</b>:\n\n"
    for lesson in lessons:
        response += (
            f"🔸 <b>{lesson['lesson_number']}. {lesson['time']}</b>\n"
            f" <b>Предмет:</b> {lesson['subject']}\n"
            f" <b>Викладач:</b> <b>{lesson['teacher']}</b>\n"
            f" <b>Аудиторія:</b> <b>{lesson['room']}</b>\n\n"
        )
    
    await message.answer(response, parse_mode="HTML")

@dp.message(Command("week"))
async def cmd_week(message: types.Message):
    schedule = load_schedule_cache()

    if not schedule:
        await message.answer("🚫Розклад не знайдено. Спробуй пізніше.")
        return

    response = "Розклад на тиждень:\n\n"
    for day, lessons in schedule.items():
        response += f"📅 <b>{day}</b>:\n"
        if lessons:
            for lesson in lessons:
                response += (
                    f"🔸 <b>{lesson['lesson_number']}. {lesson['time']}</b>\n"
                    f" <b>Предмет:</b> {lesson['subject']}\n"
                    f" <b>Викладач:</b> <b>{lesson['teacher']}</b>\n"
                    f" <b>Аудиторія:</b> <b>{lesson['room']}</b>\n\n"
                )
        else:
            response += "😃 Пар немає\n\n"

    await message.answer(response, parse_mode="HTML")
