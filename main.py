from config import VK_TOKEN, DATABASE_PATH, CHAT_ID
from src.core.bot import RedemptionBot
from src.core.message_handler import MessageHandler
from src.database.database import DatabaseHandler
from src.database.timetable import Timetable
from src.reminder_handler.reminder_handler import ReminderHandler
from src.vk.API_handler import VkApiHandler

if __name__ == '__main__':
    database = DatabaseHandler(DATABASE_PATH)
    timetable = Timetable(database)
    vk = VkApiHandler(VK_TOKEN, CHAT_ID)
    message_handler = MessageHandler(vk, timetable)
    reminder_handler = ReminderHandler(vk, timetable, message_handler)

    bot = RedemptionBot(vk, message_handler, reminder_handler)

    bot.start_bot()
