from src.database.database import Timetable
from src.vk.API_handler import VkApiHandler
from src.reminder_handler.reminder_handler import ReminderHandler
from src.core.message_handler import MessageHandler


class RedemptionBot:
    def __init__(self, timetable: Timetable, vk: VkApiHandler,
                 message_handler: MessageHandler, reminder_handler: ReminderHandler):
        self.timetable = timetable
        self.vk = vk
        self.message_handler = message_handler
        self.reminder_handler = reminder_handler

    def start_reminding(self):
        self.reminder_handler.start_reminding()

    def start_polling(self):
        pass

    def start_bot(self):
        self.start_polling()
        self.start_reminding()
