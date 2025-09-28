import unittest
from unittest.mock import patch, MagicMock
from src.calendar_sync import sync_calendar_task, get_schedule_hash, save_schedule_hash, load_schedule_hash
from src.parser import save_schedule_cache

class TestCalendarSync(unittest.TestCase):

    def setUp(self):
        test_schedule = {
            "Понеділок": [
                {
                    "lesson_number": "1",
                    "time": "08:00-09:35",
                    "subject": "Тестова пара",
                    "teacher": "Викладач",
                    "room": "ауд. 101",
                    "activity": "Лекція"  # ✅ Додано
                }
            ]
        }
        save_schedule_cache(test_schedule)

    @patch("os.getenv")
    @patch("src.calendar_sync.get_calendar_service")
    def test_sync_calendar_task(self, mock_get_service, mock_getenv):
        mock_getenv.return_value = "test@group.calendar.google.com"
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        # Викликаємо функцію
        sync_calendar_task()

        # Перевіряємо, чи викликалася функція
        mock_get_service.assert_called()

    def test_get_schedule_hash(self):
        schedule = {"test": "data"}
        hash_value = get_schedule_hash(schedule)
        self.assertIsInstance(hash_value, str)
        self.assertEqual(len(hash_value), 32)  # MD5

    def test_save_and_load_schedule_hash(self):
        test_hash = "abcd1234"
        save_schedule_hash(test_hash)
        loaded_hash = load_schedule_hash()
        self.assertEqual(loaded_hash, test_hash)