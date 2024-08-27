from dataclasses import dataclass

import dacite
import requests
from dacite import from_dict

from src import py_day
from src.core.logger.logger import logger
from src.database.database import DatabaseHandler


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

    def get_lesson_numbers(self) -> list[str]:
        numbers = []
        for lesson in self.lessons:
            numbers.append(lesson.class_number)
        return numbers

    def get_lesson(self, number: int | str) -> Lesson | None:
        numbers = self.get_lesson_numbers()
        try:
            return self.lessons[numbers.index(str(number))]
        except ValueError:
            return


class Timetable:
    def __init__(self, database: DatabaseHandler) -> None:
        self._database = database

    def get_lessons_for_day(self, day: py_day.Day = None) -> Day:
        if day is None:
            day = py_day.today()

        lessons = self._database.get_classes(day.weekday, day.week_type)

        return from_dict(Day, lessons)

    def change_database(self, file: dict[str: str | dict]) -> None:
        if file['type'] != 'doc':
            logger.error('Wrong file type when changing database, got %s', file['type'])
            return

        file = file['doc']

        if file['ext'] != 'json':
            logger.error('Wrong file type when changing database, got %s', file['ext'])
            return

        url = file['url']
        with requests.get(url, stream=True) as request:
            request.raise_for_status()
            self._database.change_database(request.json())

    def remove_lesson(self, week_type, weekday, class_number) -> Lesson | None:

        lesson = self._database.remove_class(week_type, weekday, class_number)
        if lesson:
            lesson = dacite.from_dict(Lesson, lesson)

        return lesson

    def add_lesson(self,
                   week_type: str,
                   weekday: str,
                   class_number: int | str,
                   start_time: str,
                   end_time: str,
                   class_name: str,
                   room_number: str,
                   prof_name: str,
                   url: str) -> str:

        lesson = self.remove_lesson(week_type, weekday, class_number)
        answer = ''
        if lesson:
            answer = f'Удалена пара {lesson.class_number} — {lesson.class_name}, добавлена пара {class_name}'

        self._database.add_class(week_type, weekday, class_number,
                                 start_time, end_time,
                                 class_name, room_number,
                                 prof_name, url)

        if not answer:
            answer = f'Добавлена пара {class_name}'

        return answer
