from datetime import datetime

from src.core.logger.logger import logger
from src.core.strings import add_edit_class_usage
from src.database.timetable import Timetable
from src import py_day
from src.vk.API_handler import Message
from src.vk.API_handler import VkApiHandler


class MessageHandler:
    def __init__(self, vk: VkApiHandler, timetable: Timetable):
        self._vk = vk
        self._timetable = timetable

    def send_schedule_for_day(self, day: datetime = None, peer_id: int = None) -> None:
        if day is None:
            day = py_day.today()
        lessons = self._timetable.get_lessons_for_day(day)
        formatted_lessons = lessons.format()

        self._vk.send_message(formatted_lessons, peer_id)

    def add_edit_class_check(self, message: Message) -> None:
        args = message.text.split('\n')
        command = args.pop(0)
        usage = f'\n{command}\n{add_edit_class_usage}'

        if not args:
            self._vk.send_message(f'Не переданы аргументы. Использование команды: {usage}',
                                  message.peer_id)
        elif len(args) != 10:
            self._vk.send_message(f'Неверное количество аргументов. Использование команды: {usage}',
                                  message.peer_id)
        else:
            try:
                if command == '/edit_class':
                    answer = self._timetable.edit_lesson(args)
                else:
                    answer = self._timetable.add_lesson(args)
            except ValueError as e:
                answer = f'Ошибка: {e}. Использование команды: {usage}'

            self._vk.send_message(answer, message.peer_id)

    def check_message(self, message: Message) -> None:
        text = message.text

        if text.lower() == 'чекай':
            self._vk.send_message('чекаю', message.peer_id)

        elif text.startswith('/edit_class') or text.startswith('/add_class'):
            self.add_edit_class_check(message)

    def handle_messages(self, messages: list[Message]) -> None:
        for message in messages:
            logger.info('Received message: %s', message)
            self.check_message(message)
