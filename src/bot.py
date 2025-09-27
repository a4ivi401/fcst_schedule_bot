from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from dotenv import load_dotenv
import os

from src.parser import parse_schedule

# Завантажуємо змінні з .env
load_dotenv()

# Отримуємо токен з .env
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Токен бота не знайдено в .env файлі")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Я бот для перегляду розкладу. Використовуй /today або /week.")

@dp.message(Command("today"))
async def cmd_today(message: types.Message):
    url = "https://portal.nau.edu.ua/schedule/group?id=4349"
    schedule = parse_schedule(url)

    if not schedule:
        await message.answer("Не вдалося отримати розклад.")
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
        await message.answer(f"Сьогодні ({today_name}) пар немає.")
        return

    response = f"Розклад на {today_name}:\n"
    for lesson in lessons:
        response += f"{lesson['time']} — {lesson['subject']}\n"
        response += f"  Викладач: {lesson['teacher']}\n"
        response += f"  Аудиторія: {lesson['room']}\n\n"
    
    await message.answer(response)

@dp.message(Command("week"))
async def cmd_week(message: types.Message):
    url = "https://portal.nau.edu.ua/schedule/group?id=4349"
    schedule = parse_schedule(url)

    if not schedule:
        await message.answer("Не вдалося отримати розклад.")
        return

    response = "Розклад на тиждень:\n\n"
    for day, lessons in schedule.items():
        response += f"📅 {day}:\n"
        if lessons:
            for lesson in lessons:
                response += f"  {lesson['time']} — {lesson['subject']}\n"
                response += f"    Викладач: {lesson['teacher']}\n"
                response += f"    Аудиторія: {lesson['room']}\n\n"
        else:
            response += "  Пар немає\n\n"

    await message.answer(response)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
