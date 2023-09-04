import json
from src.database.weekday_translation import weekday_translation, week_types


class DatabaseHandler:
    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path
        self.timetable = None
        self.__load_schedule()
        self.check_database()

    def __load_schedule(self) -> None:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.timetable = json.load(f)

    def __save_schedule(self) -> None:
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.timetable, f, indent=4, ensure_ascii=False)

    def check_database(self):
        for week_type in week_types:
            if week_type not in self.timetable:
                self.timetable[week_type] = {}
            for weekday in weekday_translation.values():
                if weekday not in self.timetable[week_type]:
                    self.timetable[week_type][weekday] = {'day_name': weekday, 'lessons': []}

        self.__save_schedule()

    def get_classes(self,
                    weekday: str,
                    week_type: str) -> dict[str, dict[str, str]]:

        return self.timetable.get(week_type, {}).get(weekday, {})

    def add_class(self,
                  week_type: str,
                  day: str,
                  number: int,
                  start_time: str,
                  end_time: str,
                  class_name: str,
                  room_number: str,
                  prof_name: str,
                  url: str) -> None:

        day = day.capitalize()
        number = str(number)

        self.timetable[week_type][day]['lessons'].append({'class_number': number,
                                                          'start_time': start_time, 'end_time': end_time,
                                                          'class_name': class_name,
                                                          'room_number': room_number, 'prof_name': prof_name,
                                                          'url': url})
        self.__save_schedule()

    def remove_class(self,
                     week_type: str,
                     day: str,
                     number: int) -> None:

        day = day.capitalize()
        number = str(number)

        if week_type in self.timetable and day in self.timetable[week_type]:

            if number in self.timetable[week_type][day]:
                del self.timetable[week_type][day][number]
                self.__save_schedule()
