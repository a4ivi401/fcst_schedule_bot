import unittest
from unittest.mock import patch, mock_open
from src.parser import parse_schedule, get_current_week_type, run_parser, save_schedule_cache
import json
import os

class TestParser(unittest.TestCase):

    @patch("requests.get")
    def test_parse_schedule(self, mock_get):
        # Симуляція HTML-відповіді
        html_content = '''
        <div class="wrapper"><h2>Тиждень 1</h2><table class="schedule">
        <thead><tr><th class="day-name">Понеділок</th></tr></thead>
        <tbody>
            <tr><th class="hour-name"><div class="name">1</div><div class="full-name">08:00-09:35</div></th>
                <td><div class="pairs"><div class="pair">
                    <div class="subject">Тестова пара</div>
                    <div class="teacher">Викладач</div>
                    <div class="room">ауд. 101</div>
                </div></div></td>
            </tr>
        </tbody>
        </table></div>
        '''
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html_content

        result = parse_schedule("http://example.com")
        self.assertIn("Понеділок", result)
        self.assertEqual(result["Понеділок"][0]["subject"], "Тестова пара")

    def test_get_current_week_type(self):
        week = get_current_week_type()
        self.assertIn(week, ["week1", "week2"])

    @patch("src.parser.parse_schedule")
    def test_run_parser(self, mock_parse):
        mock_parse.return_value = {"Понеділок": []}
        run_parser()
        mock_parse.assert_called_once()

    def test_save_schedule_cache(self):
        test_schedule = {"Понеділок": []}
        save_schedule_cache(test_schedule)
        self.assertTrue(os.path.exists("data/schedule_cache.json"))
        with open("data/schedule_cache.json", "r", encoding="utf-8") as f:
            saved = json.load(f)
        self.assertEqual(saved, test_schedule)