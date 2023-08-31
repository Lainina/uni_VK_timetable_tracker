import time
from typing import Type
import re

from src.reminder_handler import py_day

import schedule
from schedule import CancelJob

from config import REMINDER_DELAY, DAILY_REMINDER_TIME, DAILY_SCHEDULING_TIME, TIMEZONE
from src.vk.API_handler import VkApiHandler
from src.core.message_handler import MessageHandler
from src.database.database import Timetable
from src.core.logger.logger import logger


class ReminderHandler:
    def __init__(self, vk: VkApiHandler, timetable: Timetable, message_handler: MessageHandler):
        self._vk = vk
        self._timetable = timetable
        self._message_handler = message_handler

    def send_reminder(self, text, delete_time) -> Type[CancelJob]:

        match = re.search(r"пара — [\w. -]+", text)
        logger.info('Sending reminder: %s', match[0][7:] if match else 'Not found')

        reminder_id = self._vk.send_message(text)
        schedule.every().day.at(delete_time, TIMEZONE).do(self.delete_reminder, reminder_id=reminder_id)

        return schedule.CancelJob

    def delete_reminder(self, reminder_id: int) -> Type[CancelJob]:
        logger.info('Deleting reminder...')
        self._vk.delete_message(reminder_id)

        return schedule.CancelJob

    def schedule_reminder(self, lesson: dict[str, str]) -> None:
        reminder = (
            f"Через {abs(REMINDER_DELAY)} минут начнётся пара — {lesson['class_name']}"
            f"\nПреподаватель — {lesson['prof_name']}"
            f"\nСсылка: {lesson['url']}")

        logger.info('Scheduling reminder: %s', lesson['class_name'])

        start_time = lesson['start_time']
        end_time = lesson['end_time']

        send_time = py_day.delta_minutes(start_time, REMINDER_DELAY)

        schedule.every().day.at(send_time, TIMEZONE).do(self.send_reminder, text=reminder, delete_time=end_time)

    def schedule_day(self, day=py_day.today()) -> None:
        lessons = self._timetable.get_classes_for_day(day)

        for lesson in lessons:
            self.schedule_reminder(lessons[lesson])

    def reset_reminders(self) -> Type[CancelJob]:
        schedule.clear()
        self.schedule_every_day()

        return CancelJob

    def deal_with_today(self) -> None:
        now = py_day.today().strftime('%H:%M')

        if now == DAILY_REMINDER_TIME:
            self._message_handler.send_schedule_for_day(py_day.tomorrow())

        elif DAILY_SCHEDULING_TIME <= now < DAILY_REMINDER_TIME:
            self.schedule_day(py_day.today())
            schedule.every().day.at(DAILY_REMINDER_TIME).do(self.reset_reminders())

    def schedule_every_day(self) -> None:
        schedule.every().day.at(DAILY_SCHEDULING_TIME).do(self.schedule_day)
        schedule.every().day.at(DAILY_REMINDER_TIME).do(self._message_handler.send_schedule_for_day, py_day.tomorrow())

    def start_reminding(self) -> None:

        self.deal_with_today()

        self.schedule_every_day()

        while True:
            schedule.run_pending()
            time.sleep(1)
