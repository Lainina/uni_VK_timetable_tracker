from dataclasses import dataclass

from dacite import from_dict

from src.database.database import DatabaseHandler
from src.database.weekday_translation import weekday_translation
from src.reminder_handler import py_day


@dataclass(frozen=True)
class Lesson:
    class_number: str
    start_time: str
    end_time: str
    class_name: str
    room_number: str
    prof_name: str
    url: str

    def format(self, reminder_delay) -> str:
        formatted_lesson = f'Через {abs(reminder_delay)} минут начнётся пара — {self.class_name}'

        if self.room_number:
            formatted_lesson += f' (ауд. {self.room_number})'

        formatted_lesson += f'\nПреподаватель — {self.prof_name}'

        if self.url:
            formatted_lesson += f'\nСсылка: {self.url}'

        return formatted_lesson


@dataclass(frozen=True)
class Day:
    day_name: str
    lessons: list[Lesson]

    def format(self) -> str:
        day = self.day_name.lower()  # TODO: find a more pythonic way to do this
        if day[-1] == 'а':
            day = day[:-1] + 'у'

        formatted_classes = f'Расписание на {day}:'

        if self.lessons:
            for lesson in self.lessons:
                formatted_classes += (f'\n{lesson.class_number} пара ({lesson.start_time}-{lesson.end_time}) — '
                                      f'{lesson.class_name}')
        else:
            formatted_classes += '\nПар нет 🎉'

        return formatted_classes


class Timetable:
    def __init__(self, database: DatabaseHandler) -> None:
        self._database = database

    @staticmethod
    def translate_weekday(weekday: str) -> str:
        return weekday_translation[weekday]

    def get_classes_for_day(self, day=None) -> Day:
        if day is None:
            day = py_day.today()
        weekday = self.translate_weekday(day.strftime('%A'))
        week_type = py_day.week_type(day)

        classes = self._database.get_classes(weekday, week_type)

        return from_dict(Day, classes)
