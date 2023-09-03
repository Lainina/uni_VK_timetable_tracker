import time
from threading import Thread

from requests.exceptions import ConnectionError

from src.core.logger.logger import logger
from src.core.message_handler import MessageHandler
from src.reminder_handler.reminder_handler import ReminderHandler
from src.vk.API_handler import VkApiHandler


class RedemptionBot:
    def __init__(self, vk: VkApiHandler,
                 message_handler: MessageHandler, reminder_handler: ReminderHandler):
        self.vk = vk
        self.message_handler = message_handler
        self.reminder_handler = reminder_handler

    def start_reminding(self) -> None:
        self.reminder_handler.start_reminding()

    def start_polling(self):
        server = self.vk.get_first_server()
        logger.info('Connected to server, polling...')

        while True:
            try:
                server, messages = self.vk.poll(server)
            except RuntimeError:
                logger.critical('Longpoll connection terminated')
                raise
            except ConnectionError:
                logger.error('Got a Connection Error, retrying...')
                time.sleep(5)
                continue

            if messages:
                for message in messages:
                    logger.info('Received message: %s', message)
                    pass  # TODO: handle messages somehow

    def start_bot(self):
        thread_1 = Thread(target=self.start_polling)
        thread_2 = Thread(target=self.start_reminding)

        thread_1.start()
        thread_2.start()
