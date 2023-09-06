from datetime import datetime

from src.core.logger.logger import logger
from src.database.timetable import Timetable
from src.reminder_handler import py_day
from src.vk.API_handler import Message
from src.vk.API_handler import VkApiHandler


class MessageHandler:
    def __init__(self, vk: VkApiHandler, timetable: Timetable):
        self._vk = vk
        self._timetable = timetable

    def send_schedule_for_day(self, day: datetime = None, peer_id: int = None) -> None:
        if day is None:
            day = py_day.today()
        classes = self._timetable.get_classes_for_day(day)
        formatted_classes = classes.format()

        self._vk.send_message(formatted_classes)
        self._vk.send_message(formatted_classes, peer_id)

    def check_message(self, message: Message) -> None:
        text = message.text

    def handle_messages(self, messages: list[Message]) -> None:
        for message in messages:
            logger.info('Received message: %s', message)
            self.check_message(message)
