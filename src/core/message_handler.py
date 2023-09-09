from datetime import datetime

from src import py_day
from src.core.button_handler import ButtonHandler
from src.core.logger.logger import logger
from src.core.observable import Observable
from src.database.timetable import Timetable
from src.vk.API_handler import Message, MessageEvent
from src.vk.API_handler import VkApiHandler


class MessageHandler(Observable):
    def __init__(self, vk: VkApiHandler, timetable: Timetable, button_handler: ButtonHandler):
        super().__init__()
        self._vk = vk
        self._timetable = timetable
        self._button_handler = button_handler

    def send_schedule_for_day(self, day: datetime = None, peer_id: int = None) -> None:
        if day is None:
            day = py_day.today()
        lessons = self._timetable.get_lessons_for_day(day)
        formatted_lessons = lessons.format()

        self._vk.send_message(formatted_lessons, peer_id)

    def check_message(self, message: Message) -> None:
        text = message.text

        if text.lower() == 'чекай':
            self._vk.send_message('чекаю', message.peer_id)
        elif text.lower() == '/edit':
            self._button_handler.start_keyboard()

    def handle_messages(self, messages: list[Message]) -> None:
        for message in messages:
            logger.info('Received message: %s', message)
            self.check_message(message)

    def handle_events(self, message_events: list[MessageEvent]) -> None:
        self._button_handler.handle_events(message_events)
