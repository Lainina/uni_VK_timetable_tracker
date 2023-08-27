import time
from typing import Type

import schedule
from datetime import datetime, timedelta

from schedule import CancelJob

from config import REMINDER_DELAY, DAILY_REMINDER_TIME, TIMEZONE
from src.vk.API_handler import VkApiHandler
from src.core.message_handler import MessageHandler


class ReminderHandler:
    def __init__(self, vk: VkApiHandler, message_handler: MessageHandler):
        self._vk = vk
        self._message_handler = message_handler

    def send_reminder(self, text, delete_time) -> Type[CancelJob]:
        reminder_id = self._vk.send_message(text)
        schedule.every().day.at(delete_time).do(self.delete_reminder, reminder_id=reminder_id)

        return schedule.CancelJob

    def delete_reminder(self, reminder_id: int) -> Type[CancelJob]:
        self._vk.delete_message(reminder_id)

        return schedule.CancelJob

    def schedule_reminder(self, lesson: dict[str, str]) -> None:
        reminder = (
            f"Через {abs(REMINDER_DELAY)} минут начнётся пара — {lesson['class_name']} (ауд. {lesson['room_number']})"
            f"\nПреподаватель — {lesson['prof_name']}")

        start_time = lesson['start_time']
        end_time = lesson['end_time']

        send_time = (datetime.strptime(start_time, '%H:%M')
                     + timedelta(minutes=REMINDER_DELAY)).strftime('%H:%M')

        schedule.every().day.at(send_time).do(self.send_reminder, text=reminder, delete_time=end_time)

    def prep_the_day(self) -> None:
        tomorrow = datetime.now(TIMEZONE) + timedelta(days=1)

        lessons = self._message_handler.send_schedule_for_day(tomorrow)

        for lesson in lessons:
            self.schedule_reminder(lessons[lesson])

    def start_reminding(self) -> None:
        # TODO: schedule lessons that are today on start
        schedule.every().day.at(DAILY_REMINDER_TIME).do(self.prep_the_day)

        while True:
            schedule.run_pending()
            time.sleep(1)
