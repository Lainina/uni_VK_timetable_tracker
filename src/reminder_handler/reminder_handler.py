import re
import time
from typing import Type

import schedule
from schedule import CancelJob

from config import REMINDER_DELAY, DAILY_REMINDER_TIME, DAILY_SCHEDULING_TIME, TIMEZONE
from src.core.logger.logger import logger
from src.core.message_handler import MessageHandler
from src.database.timetable import Timetable, Lesson
from src.reminder_handler import py_day
from src.vk.API_handler import VkApiHandler


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

    def schedule_reminder(self, lesson: Lesson) -> None:
        reminder = lesson.format(REMINDER_DELAY)

        start_time = lesson.start_time
        end_time = lesson.end_time

        send_time = py_day.delta_minutes(start_time, REMINDER_DELAY)

        logger.info('Scheduling reminder at %s: %s', send_time, lesson.class_name)

        schedule.every().day.at(send_time, TIMEZONE).do(self.send_reminder, text=reminder, delete_time=end_time)

    def schedule_day(self, day=None) -> None:
        if day is None:
            day = py_day.today()

        day_schedule = self._timetable.get_classes_for_day(day)

        for lesson in day_schedule.lessons:
            self.schedule_reminder(lesson)

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
            schedule.every().day.at(DAILY_REMINDER_TIME).do(self.reset_reminders)

    def schedule_every_day(self) -> None:
        schedule.every().day.at(DAILY_SCHEDULING_TIME).do(self.schedule_day)
        schedule.every().day.at(DAILY_REMINDER_TIME).do(self._message_handler.send_schedule_for_day, py_day.tomorrow())

    def start_reminding(self) -> None:

        self.deal_with_today()

        self.schedule_every_day()

        while True:
            schedule.run_pending()
            time.sleep(1)
