import json
from datetime import datetime
import locale


locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


class Timetable:
    def __init__(self, filename: str) -> None:
        self.filename: str = filename
        self.timetable = None
        self.load_schedule()

    def load_schedule(self) -> None:
        with open(self.filename, 'r', encoding='utf-8') as f:
            self.timetable = json.load(f)

    def save_schedule(self) -> None:
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.timetable, f, indent=4, ensure_ascii=False)

    def get_classes(self,
                    day: str,
                    week_type: str) -> dict[str, str]:

        day = day.capitalize()

        return self.timetable.get(week_type, {}).get(day, {})

    def get_classes_for_today(self) -> dict[str, str]:
        today = datetime.today().strftime('%A')
        week_number = datetime.today().isocalendar()[1]

        week_type = 'odd' if week_number % 2 == 1 else 'even'

        return self.get_classes(today, week_type)

    def add_class(self,
                  week_type: str,
                  day: str,
                  number: int,
                  start_time: str,
                  end_time: str,
                  class_name: str,
                  room_number: str,
                  prof_name: str) -> None:

        day = day.capitalize()
        number = str(number)

        if week_type not in self.timetable:
            self.timetable[week_type] = {}

        if day not in self.timetable[week_type]:
            self.timetable[week_type][day] = {}

        if number not in self.timetable[week_type][day]:
            self.timetable[week_type][day][number] = {}

        self.timetable[week_type][day][number] = {'start_time': start_time, 'end_time': end_time,
                                                  'class_name': class_name,
                                                  'room_number': room_number, 'prof_name': prof_name}
        self.save_schedule()

    def remove_class(self,
                     week_type: str,
                     day: str,
                     number: int) -> None:

        day = day.capitalize()
        number = str(number)

        if week_type in self.timetable and day in self.timetable[week_type]:

            if number in self.timetable[week_type][day]:
                del self.timetable[week_type][day][number]
                self.save_schedule()


timetable = Timetable('timetable.json')
