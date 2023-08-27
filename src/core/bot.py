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

    def start_reminding(self) -> None:
        self.reminder_handler.start_reminding()

    def start_polling(self):
        server = self.vk.get_first_server()

        while True:
            try:
                server, messages = self.vk.poll(server)
            except RuntimeError:
                print('terminal error: longpoll connection terminated')
                raise

            if messages:
                for message in messages:
                    pass  # TODO: handle messages somehow

    def start_bot(self):
        self.start_polling()
        self.start_reminding()
