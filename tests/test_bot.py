import unittest
from unittest.mock import AsyncMock, patch
from aiogram import types
from src.bot import cmd_today, cmd_tomorrow, cmd_week, cmd_calendar_link
from src.parser import save_schedule_cache

class TestBot(unittest.TestCase):

    def setUp(self):
        # Створюємо тестовий розклад
        test_schedule = {
            "Понеділок": [
                {
                    "lesson_number": "1",
                    "time": "08:00-09:35",
                    "subject": "Тестова пара",
                    "teacher": "Викладач",
                    "room": "ауд. 101"
                }
            ],
            "Вівторок": []
        }
        save_schedule_cache(test_schedule)

    async def test_cmd_today(self):
        message = AsyncMock()
        message.answer = AsyncMock()
        await cmd_today(message)
        message.answer.assert_called()

    async def test_cmd_tomorrow(self):
        message = AsyncMock()
        message.answer = AsyncMock()
        await cmd_tomorrow(message)
        message.answer.assert_called()

    async def test_cmd_week(self):
        message = AsyncMock()
        message.answer = AsyncMock()
        await cmd_week(message)
        message.answer.assert_called()

    @patch("os.getenv")
    async def test_cmd_calendar_link(self, mock_getenv):
        mock_getenv.return_value = "test@group.calendar.google.com"
        message = AsyncMock()
        message.answer = AsyncMock()
        await cmd_calendar_link(message)
        message.answer.assert_called()