import json

from src.core.logger.logger import logger
from src.database.timetable import Timetable
from src.vk.API_handler import MessageEvent
from src.vk.API_handler import VkApiHandler
from config import TEST_USER_ID


class Keyboards:
    def __init__(self, file_path: str):
        self.file_path: str = file_path
        self.__keyboards = None
        self.__get_keyboards()

    def __get_keyboards(self) -> None:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.keyboards = json.load(f)

    def get_keyboard(self, keyboard_name: str) -> dict:
        keyboard = self.keyboards[keyboard_name]
        formatted_keyboard = json.dumps(keyboard, ensure_ascii=False, separators=(',', ':'))

        return {'keyboard': formatted_keyboard}


class ButtonHandler:
    def __init__(self, vk: VkApiHandler, timetable: Timetable):
        self._vk = vk
        self._timetable = timetable
        self._keyboards = Keyboards(r'src\core\keyboards.json')

    def start_keyboard(self) -> None:
        keyboard = self._keyboards.get_keyboard('starting_keyboard')
        self._vk.send_message('Выберите команду', peer_id=TEST_USER_ID, keyboard=keyboard)

    def handle_event(self, event: MessageEvent) -> None:
        pass

    def handle_events(self, message_events: list[MessageEvent]) -> None:
        for event in message_events:
            logger.info('Received event: %s', event)
            self.handle_event(event)
