from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv 

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    credentials_path = 'credentials.json'
    if not os.path.exists(credentials_path):
        raise FileNotFoundError("Файл credentials.json не знайдено")

    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    return service

def load_schedule_cache():
    path = 'data/schedule_cache.json'
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_schedule_hash(hash_value):
    os.makedirs('data', exist_ok=True)
    with open('data/schedule_hash.txt', 'w') as f:
        f.write(hash_value)

def load_schedule_hash():
    path = 'data/schedule_hash.txt'
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        return f.read().strip()

def get_schedule_hash(schedule):
    import hashlib
    json_str = json.dumps(schedule, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(json_str.encode('utf-8')).hexdigest()

def get_target_week_start():
    """
    Визначає початок тижня:
    - Якщо сьогодні субота/неділя → повертаємо понеділок наступного тижня.
    - Якщо будні → повертаємо понеділок цього тижня.
    """
    now = datetime.now()
    if now.weekday() >= 5:  # 5 — субота, 6 — неділя
        # Понеділок наступного тижня
        days_ahead = 7 - now.weekday()
        return now + timedelta(days=days_ahead)
    else:
        # Понеділок цього тижня
        return now - timedelta(days=now.weekday())

def delete_week_events(service, calendar_id, week_start):
    # Визначаємо діапазон тижня: понеділок 00:00 до неділі 23:59
    week_end = week_start + timedelta(days=6)

    time_min = week_start.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
    time_max = week_end.replace(hour=23, minute=59, second=59).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    for event in events:
        service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
    print(f"✅ Видалено {len(events)} подій за тиждень з {week_start.strftime('%d.%m.%Y')} по {week_end.strftime('%d.%m.%Y')}.")

def create_calendar_events(schedule, calendar_id, service, week_start):
    for day, lessons in schedule.items():
        for lesson in lessons:
            start_time = parse_time_to_datetime(lesson['time'], day, week_start)
            if not start_time:
                continue

            start_str, end_str = lesson['time'].split('-')
            start_hour, start_min = map(int, start_str.split(':'))
            end_hour, end_min = map(int, end_str.split(':'))

            start_dt = start_time.replace(hour=start_hour, minute=start_min)
            end_dt = start_time.replace(hour=end_hour, minute=end_min)

            event = {
                'summary': lesson['subject'],
                'location': lesson['room'],
                'description': f"Викладач: {lesson['teacher']}\nТип: {lesson['activity']}",
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'Europe/Kiev',
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'Europe/Kiev',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }

            service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f"✅ Створено нові події для тижня з {week_start.strftime('%d.%m.%Y')}.")

def parse_time_to_datetime(time_str, day_str, week_start):
    day_map = {
        "Понеділок": 0,
        "Вівторок": 1,
        "Середа": 2,
        "Четвер": 3,
        "П'ятниця": 4,
        "Субота": 5,
        "Неділя": 6
    }

    target_weekday = day_map.get(day_str)
    if target_weekday is None:
        return None

    target_date = week_start + timedelta(days=target_weekday)
    return target_date

def sync_calendar_task():
    load_dotenv()  # ✅ Додаємо це перед зчитуванням змінної
    calendar_id = os.getenv("CALENDAR_ID")
    if not calendar_id:
        raise ValueError("CALENDAR_ID не знайдено в .env")

    schedule = load_schedule_cache()
    if not schedule:
        print("❌ Розклад не знайдено для синхронізації.")
        return

    current_hash = get_schedule_hash(schedule)
    previous_hash = load_schedule_hash()

    if current_hash != previous_hash:
        print("🔄 Розклад змінився. Оновлюємо календар...")
        service = get_calendar_service()

        # Визначаємо, який тиждень оновлювати
        week_start = get_target_week_start()
        print(f"🎯 Цільовий тиждень: з {week_start.strftime('%d.%m.%Y')}")

        delete_week_events(service, calendar_id, week_start)
        create_calendar_events(schedule, calendar_id, service, week_start)
        save_schedule_hash(current_hash)
    else:
        print("✅ Розклад не змінився. Пропускаємо синхронізацію.")