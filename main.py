from src.database.timetable import Timetable
from src.database.database import DatabaseHandler
from config import VK_TOKEN, DATABASE_PATH, ON_REPL
from src.vk.API_handler import VkApiHandler
from src.reminder_handler.reminder_handler import ReminderHandler
from src.core.bot import RedemptionBot
from src.core.message_handler import MessageHandler
from src.server.background import keep_alive

if __name__ == '__main__':
    database = DatabaseHandler(DATABASE_PATH)
    timetable = Timetable(database)
    vk = VkApiHandler(VK_TOKEN)
    message_handler = MessageHandler(vk, timetable)
    reminder_handler = ReminderHandler(vk, timetable, message_handler)

    bot = RedemptionBot(vk, message_handler, reminder_handler)

    if ON_REPL:
        keep_alive()

    bot.start_bot()
