from datetime import datetime
from src.vk.API_handler import VkApiHandler
from src.database.database import Timetable
from config import TIMEZONE


class MessageHandler:
    def __init__(self, vk: VkApiHandler, timetable: Timetable):
        self._vk = vk
        self._timetable = timetable

    @staticmethod
    def format(lessons: dict[str, dict[str, str]], day: str) -> str:
        day = day.lower()   # TODO: find a more pythonic way to do this
        if day[-1] == 'а':
            day = day[:-1] + 'у'

        formatted_classes = f'Расписание на {day}:'

        if lessons:
            for lesson_number in lessons:
                lesson = lessons[lesson_number]
                formatted_classes += (f'\n{lesson_number} пара ({lesson["start_time"]}-{lesson["end_time"]}) — '
                                      f'{lesson["class_name"]} (ауд. {lesson["room_number"]})')
        else:
            formatted_classes += '\nПар нет 🎉'

        return formatted_classes

    def send_schedule_for_day(self, day=datetime.now(TIMEZONE)) -> dict[str, dict[str, str]]:

        classes = self._timetable.get_classes_for_day(day)

        weekday = self._timetable.translate_weekday(day.strftime('%A'))
        formatted_classes = self.format(classes, weekday)

        self._vk.send_message(formatted_classes)

        return classes
