import json

from src.core.logger.logger import logger
from src.database.timetable import Timetable
from src.vk.API_handler import MessageEvent
from src.vk.API_handler import VkApiHandler
from config import TEST_USER_ID
from dataclasses import dataclass, asdict
from src.py_day import weekday_translation
from typing import Optional
from src import py_day


@dataclass
class Button:
    payload: dict
    label: str
    color: Optional[str]

    def get_button(self) -> dict:
        button = {'action': {'type': 'callback', 'payload': str(self.payload).replace("'", '"'), 'label': self.label}}
        if self.color:
            button['color'] = self.color
        return button


@dataclass
class Keyboard:
    buttons: list[[Button]]

    def format_buttons(self) -> list:
        formatted_buttons = []
        for i, row in enumerate(self.buttons):
            formatted_buttons.append([])
            for button in row:
                formatted_buttons[i].append(button.get_button())

        formatted_buttons.append([self.get_back_button().get_button()])
        return formatted_buttons

    def get_back_button(self) -> Button:
        menu = self.buttons[0][0].payload.get('menu', [])
        payload = {'command': 'back', 'menu': menu}
        button = Button(payload=payload, label='Назад', color='primary')

        return button

    def get_keyboard(self) -> dict:
        buttons = self.format_buttons()
        keyboard = {"inline": True, "buttons": buttons}
        keyboard_json = json.dumps(keyboard, ensure_ascii=False, separators=(',', ':'))

        return {'keyboard': keyboard_json}

    @staticmethod
    def from_json(file_path: str, keyboard_name: str) -> dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            keyboards = json.load(f)
        keyboard = keyboards[keyboard_name]

        keyboard_json = json.dumps(keyboard, ensure_ascii=False, separators=(',', ':'))
        return {'keyboard': keyboard_json}


class Layer:
    def __init__(self, event: MessageEvent, timetable: Timetable):
        self.event = event
        self._timetable = timetable

    @staticmethod
    def starting_layer() -> tuple[str, dict]:
        text = 'Выберите команду:'
        keyboard = Keyboard.from_json(r'src\core\keyboards.json', 'starting_keyboard')
        return text, keyboard

    def command_layer(self) -> tuple[str, dict]:
        text = 'Выберите неделю: '
        self.event.menu.append(self.event.command)
        buttons = []
        week_types = {'odd': 'Нечётная (над чертой)', 'even': 'Чётная (под чертой)'}
        for week_type in week_types:
            button = Button(payload={'command': week_type, 'menu': self.event.menu},
                            label=week_types[week_type], color=None)
            buttons.append([button])

        keyboard = Keyboard(buttons)
        return text, keyboard.get_keyboard()

    def week_layer(self) -> tuple[str, dict]:
        text = 'Выберите день: '
        self.event.menu.append(self.event.command)
        buttons = [[]]
        for weekday in weekday_translation.values():
            button = Button(payload={'command': weekday, 'menu': self.event.menu},
                            label=weekday, color=None)
            if buttons[-1]:
                buttons[-1].append(button)
                buttons.append([])
            else:
                buttons[-1].append(button)

        keyboard = Keyboard(buttons)
        return text, keyboard.get_keyboard()

    def day_layer(self) -> tuple[str, dict]:
        if self.event.menu[1] == 'add':
            pass  # TODO

        text = 'Выберите пару: '
        self.event.menu.append(self.event.command)
        buttons = []

        week_type, weekday = self.event.menu[2:]
        day = self._timetable.get_lessons_for_day(py_day.Day((week_type, weekday)))

        for lesson in day.lessons:
            button = Button(payload={'command': lesson.class_number, 'menu': self.event.menu},
                            label=lesson.class_name, color=None)
            buttons.append([button])

        if not buttons:
            text = f'Пар на {weekday} нет'
            button = Button(payload={'command': 'back', 'menu': self.event.menu},
                            label='Назад', color='primary')
            buttons.append([button])

        keyboard = Keyboard(buttons)
        return text, keyboard.get_keyboard()

    def lesson_layer(self) -> tuple[str, dict]:
        self.event.menu.append(self.event.command)
        week_type, weekday, lesson_number = self.event.menu[2:]

        if self.event.menu[1] == 'remove':
            self._timetable.remove_lesson(week_type, weekday, lesson_number)

            del self.event.menu[-1]
            self.event.command = self.event.menu.pop(-1)
            return self.day_layer()

        text = 'Выберите аттрибут: '
        buttons = [[], []]

        day = self._timetable.get_lessons_for_day(py_day.Day((week_type, weekday)))
        lesson = day.get_lesson(lesson_number)
        attributes = asdict(lesson)

        button1 = Button(payload={'command': 'class_number', 'menu': self.event.menu},
                         label=attributes['class_number'], color=None)
        button2 = Button(payload={'command': 'url', 'menu': self.event.menu},
                         label='url', color=None)
        button3 = Button(payload={'command': 'room_number', 'menu': self.event.menu},
                         label='room_number', color=None)
        buttons[0].extend([button1, button2, button3])
        del attributes['class_number']
        del attributes['url']
        del attributes['room_number']

        for attribute in attributes:
            if not attributes[attribute]:
                button = Button(payload={'command': attribute, 'menu': self.event.menu},
                                label=f'{attribute}: None', color=None)
            else:
                button = Button(payload={'command': attribute, 'menu': self.event.menu},
                                label=attributes[attribute], color=None)

            if buttons[-1]:
                buttons[-1].append(button)
                buttons.append([])
            else:
                buttons[-1].append(button)

        if not buttons[-1]:
            buttons[-1].append(buttons[-2].pop(-1))

        keyboard = Keyboard(buttons)
        return text, keyboard.get_keyboard()

    def attribute_layer(self) -> tuple[str, dict]:
        pass  # TODO

    def get_layer(self) -> tuple[str, dict]:
        match len(self.event.menu):
            case 0:
                return self.starting_layer()
            case 1:
                return self.command_layer()
            case 2:
                return self.week_layer()
            case 3:
                return self.day_layer()
            case 4:
                return self.lesson_layer()
            case 5:
                return self.attribute_layer()


class ButtonHandler:
    def __init__(self, vk: VkApiHandler, timetable: Timetable):
        self._vk = vk
        self._timetable = timetable
        self.command = None

    def start_keyboard(self) -> None:
        keyboard = Keyboard.from_json(r'src\core\keyboards.json', 'starting_keyboard')
        self._vk.send_message('Выберите команду:', peer_id=TEST_USER_ID, keyboard=keyboard)

    def handle_event(self, event: MessageEvent) -> None:
        if event.command == 'back':
            del event.menu[-1]
            event.command = event.menu.pop(-1)

        layer = Layer(event, self._timetable)
        text, keyboard = layer.get_layer()

        if keyboard:
            self._vk.edit_message(text, event.peer_id, event.message_id, keyboard=keyboard)

    def handle_events(self, message_events: list[MessageEvent]) -> None:
        for event in message_events:
            logger.debug('Received event: %s', event)
            self.handle_event(event)
