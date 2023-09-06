import time
from dataclasses import dataclass, astuple
from datetime import datetime

import dacite
from dacite import from_dict

from src import py_day
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

    def get_lessons_for_day(self, day: datetime = None) -> Day:
        if day is None:
            day = py_day.today()
        weekday = py_day.weekday(day)
        week_type = py_day.week_type(day)

        lessons = self._database.get_classes(weekday, week_type)

        return from_dict(Day, lessons)

    def add_lesson(self,
                   week_type: str,
                   day: str,
                   number: int | str,
                   start_time: str,
                   end_time: str,
                   class_name: str,
                   room_number: str,
                   prof_name: str,
                   url: str) -> None:

        lesson = self.get_lessons_for_day().get_lesson(number)

        if lesson:
            raise ValueError(f'Lesson {lesson.class_number} — {lesson.class_name} already exists')

        self._database.add_class(week_type, day, number, start_time, end_time, class_name, room_number, prof_name, url)

    def remove_lesson(self,
                      week_type: str,
                      day: str,
                      number: int | str) -> Lesson | None:

        lesson = self._database.remove_class(week_type, day, number)
        if lesson:
            lesson = dacite.from_dict(Lesson, lesson)

        return lesson

    @staticmethod
    def format_arguments(input_args) -> tuple:   # TODO: refactor this logic into smaller parts
        for i, arg in enumerate(input_args):
            if arg == '.':
                input_args[i] = ''

        day, week_type, weekday = input_args[:3]
        del input_args[:3]

        args = dict.fromkeys(['class_number', 'start_time', 'end_time',
                              'class_name', 'room_number',
                              'prof_name', 'url'])

        for value, arg in zip(input_args, args):
            args[arg] = value

        lesson = dacite.from_dict(Lesson, args)
        if day:
            if day.lower() in ('tomorrow', 'завтра'):
                day = py_day.tomorrow()
                week_type = py_day.week_type(day)
                weekday = py_day.weekday(day)
            elif day.lower() in ('today', 'сегодня'):
                day = py_day.today()
                week_type = py_day.week_type(day)
                weekday = py_day.weekday(day)
        else:
            if week_type not in py_day.week_types:
                raise ValueError
            if weekday not in py_day.weekday_translation.values():
                raise ValueError

        try:
            if int(lesson.class_number) < 1 or int(lesson.class_number) > 7:
                raise ValueError

            time.strptime(lesson.start_time, '%H:%M')
            time.strptime(lesson.end_time, '%H:%M')

            if lesson.room_number:
                int(lesson.room_number)

        except ValueError:
            raise

        if not lesson.class_name or not lesson.prof_name:
            raise ValueError

        return (week_type, weekday) + astuple(lesson)

    def edit_lesson(self, args: list) -> str:
        try:
            args = self.format_arguments(args)
        except ValueError:
            raise
        week_type, weekday, number, start_time, end_time, class_name, room_number, prof_name, url = args

        lesson = self.remove_lesson(week_type, weekday, number)
        if lesson:
            self.add_lesson(week_type, weekday, number, start_time, end_time, class_name, room_number, prof_name, url)
            return f'Удалена пара {lesson.class_number} — {lesson.class_name}, добавлена пара {class_name}'
            pass  # TODO: make a difference between edit and add

        self.add_lesson(week_type, weekday, number, start_time, end_time, class_name, room_number, prof_name, url)
        return f'Добавлена пара {class_name}'
