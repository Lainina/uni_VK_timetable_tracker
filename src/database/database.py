import json
from datetime import datetime


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
                    week_type: str) -> list[str, dict[str, str | int]]:

        day = day.capitalize()

        return self.timetable.get(week_type, {}).get(day, {})

    def get_classes_for_today(self) -> list[str, dict[str, str | int]]:
        today = datetime.today().strftime('%A')
        week_number = datetime.today().isocalendar()[1]
        week_type = 'odd' if week_number % 2 == 1 else 'even'
        return self.get_classes(today, week_type)

    def add_class(self,
                  day: str,
                  time: str,
                  class_name: str,
                  room_number: int,
                  week_type: str) -> None:

        day = day.capitalize()

        if week_type not in self.timetable:
            self.timetable[week_type] = {}

        if day not in self.timetable[week_type]:
            self.timetable[week_type][day] = {}

        self.timetable[week_type][day][time] = {'class_name': class_name, 'room_number': room_number}
        self.save_schedule()

    def remove_class(self,
                     day: str,
                     time: str,
                     week_type: str) -> None:

        day = day.capitalize()

        if week_type in self.timetable and day in self.timetable[week_type]:

            if time in self.timetable[week_type][day]:
                del self.timetable[week_type][day][time]
                self.save_schedule()


timetable = Timetable("timetable.json")
