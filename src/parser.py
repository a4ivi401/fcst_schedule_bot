import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_current_week_type():
    # Початок навчального тижня — 1 вересня 2024
    start_date = datetime(2024, 9, 1)
    today = datetime.now()

    # Кількість днів між датами
    delta = today - start_date
    weeks_passed = delta.days // 7

    # Якщо сьогодні субота або неділя, вважаємо, що вже наступний тиждень
    if today.weekday() >= 5:  # 5 — субота, 6 — неділя
        weeks_passed += 1

    # Якщо weeks_passed парне — це тиждень 1, інакше — тиждень 2
    return "week1" if weeks_passed % 2 == 0 else "week2"

def parse_schedule(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Не вдалося отримати сторінку")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Визначаємо, який тиждень зараз
    current_week = get_current_week_type()
    print(f"Поточний тиждень: {current_week.upper()}")

    # Знаходимо всі блоки з розкладом
    wrappers = soup.find_all('div', {'class': 'wrapper'})

    target_table = None
    for wrapper in wrappers:
        header = wrapper.find('h2')
        if not header:
            continue

        if "Тиждень 1" in header.get_text() and current_week == "week1":
            target_table = wrapper.find('table', {'class': 'schedule'})
            break
        elif "Тиждень 2" in header.get_text() and current_week == "week2":
            target_table = wrapper.find('table', {'class': 'schedule'})
            break

    if not target_table:
        print(f"Таблиця для {current_week} не знайдена")
        return None

    # Отримуємо назви днів тижня
    header_row = target_table.find('thead').find('tr')
    day_names = [th.get_text(strip=True) for th in header_row.find_all('th', {'class': 'day-name'})]

    # Отримуємо рядки з парами (tbody)
    rows = target_table.find_all('tr')

    schedule = {}
    for i, row in enumerate(rows):
        if i == 0:  # Пропускаємо заголовки
            continue

        cells = row.find_all(['th', 'td'])
        if not cells:
            continue

        # Час пари (наприклад, "08:00-09:35")
        time_cell = cells[0]
        time_range = time_cell.find('div', {'class': 'full-name'}).get_text(strip=True)
        lesson_number = time_cell.find('div', {'class': 'name'}).get_text(strip=True)

        # Проходимо по комірках (днях тижня)
        for j, cell in enumerate(cells[1:], start=0):  # комірки з 1 (час в 0)
            if j >= len(day_names):
                break

            day = day_names[j]
            if day not in schedule:
                schedule[day] = []

            pairs_div = cell.find('div', {'class': 'pairs'})
            if not pairs_div:
                continue

            pair_divs = pairs_div.find_all('div', {'class': 'pair'})
            for pair in pair_divs:
                subject_elem = pair.find('div', {'class': 'subject'})
                if not subject_elem:
                    continue

                subject = subject_elem.get_text(strip=True)

                teacher_elem = pair.find('div', {'class': 'teacher'})
                teacher = teacher_elem.get_text(strip=True) if teacher_elem else "Не вказано"

                room_elem = pair.find('div', {'class': 'room'})
                room = room_elem.get_text(strip=True).replace('ауд. ', '') if room_elem else "Не вказано"

                activity_tag = pair.find('div', {'class': 'activity-tag'})
                activity = activity_tag.get_text(strip=True) if activity_tag else "Не вказано"

                lesson = {
                    "lesson_number": lesson_number,
                    "time": time_range,
                    "subject": subject,
                    "activity": activity,
                    "teacher": teacher,
                    "room": room
                }
                schedule[day].append(lesson)

    return schedule

# Тест
if __name__ == "__main__":
    url = "https://portal.nau.edu.ua/schedule/group?id=4349"
    schedule = parse_schedule(url)

    if schedule:
        for day, lessons in schedule.items():
            print(f"\n{day}:")
            for lesson in lessons:
                print(f"  {lesson['time']} | {lesson['subject']} | {lesson['teacher']} | {lesson['room']}")
    else:
        print("Помилка при отриманні розкладу.")
