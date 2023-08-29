import time
from typing import Type
import re

import schedule
from datetime import datetime, timedelta

from schedule import CancelJob

from config import REMINDER_DELAY, DAILY_REMINDER_TIME, TIMEZONE
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
        schedule.every().day.at(delete_time).do(self.delete_reminder, reminder_id=reminder_id)

        return schedule.CancelJob

    def delete_reminder(self, reminder_id: int) -> Type[CancelJob]:
        logger.info('Deleting reminder...')
        self._vk.delete_message(reminder_id)

        return schedule.CancelJob

    def schedule_reminder(self, lesson: dict[str, str]) -> None:
        reminder = (
            f"Через {abs(REMINDER_DELAY)} минут начнётся пара — {lesson['class_name']} (ауд. {lesson['room_number']})"
            f"\nПреподаватель — {lesson['prof_name']}")

        logger.info('Scheduling reminder: %s', lesson['class_name'])

        start_time = lesson['start_time']
        end_time = lesson['end_time']

        send_time = (datetime.strptime(start_time, '%H:%M')
                     + timedelta(minutes=REMINDER_DELAY)).strftime('%H:%M')

        schedule.every().day.at(send_time).do(self.send_reminder, text=reminder, delete_time=end_time)

    def prep_tomorrow(self) -> None:
        tomorrow = datetime.now(TIMEZONE) + timedelta(days=1)

        lessons = self._message_handler.send_schedule_for_day(tomorrow)

        for lesson in lessons:
            self.schedule_reminder(lessons[lesson])

    def prep_today(self):
        today = datetime.now(TIMEZONE)

        lessons = self._timetable.get_classes_for_day(today)

        for lesson in lessons:
            self.schedule_reminder(lessons[lesson])

    def cancel_day(self):
        schedule.clear()
        schedule.every().day.at(DAILY_REMINDER_TIME).do(self.prep_tomorrow)

    def schedule_today(self):
        self.prep_today()

        reset_time = DAILY_REMINDER_TIME[0] + str(int(DAILY_REMINDER_TIME[1]) - 1) + DAILY_REMINDER_TIME[2:]

        schedule.every().day.at(reset_time).do(self.cancel_day)

    def start_reminding(self) -> None:
        self.schedule_today()

        schedule.every().day.at(DAILY_REMINDER_TIME).do(self.prep_tomorrow)

        while True:
            schedule.run_pending()
            time.sleep(1)
