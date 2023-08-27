from datetime import datetime
from src.vk.API_handler import VkApiHandler
from src.database.database import Timetable


class MessageHandler:
    def __init__(self, vk: VkApiHandler, timetable: Timetable):
        self._vk = vk
        self._timetable = timetable

    @staticmethod
    def format(classes: dict[str, dict[str, str]]) -> str:
        formatted_classes = str(classes)  # TODO: format the classes

        return formatted_classes

    def send_schedule_for_day(self, day=datetime.today()) -> dict[str, dict[str, str]]:

        classes = self._timetable.get_classes_for_day(day)
        formatted_classes = self.format(classes)

        self._vk.send_message(formatted_classes)

        return classes
