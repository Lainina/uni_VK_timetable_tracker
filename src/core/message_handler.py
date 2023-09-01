from src.database.timetable import Timetable
from src.reminder_handler import py_day
from src.vk.API_handler import VkApiHandler


class MessageHandler:
    def __init__(self, vk: VkApiHandler, timetable: Timetable):
        self._vk = vk
        self._timetable = timetable

    def send_schedule_for_day(self, day=py_day.today()) -> None:
        classes = self._timetable.get_classes_for_day(day)
        formatted_classes = classes.format()

        self._vk.send_message(formatted_classes)
