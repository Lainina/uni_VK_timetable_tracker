# RENAME THE FILE TO config.py

import pathlib

import pytz

TIMEZONE = pytz.timezone('Europe/Moscow')

VK_TOKEN = 'your_token'

UNI_CHAT_ID = 2000000001

TEST_CHAT_ID_1 = 2000000002
TEST_CHAT_ID_2 = 2000000003

CHAT_ID = UNI_CHAT_ID

REMINDER_DELAY = -5

PATH = str(pathlib.Path(__file__).parent.resolve())
DATABASE_PATH = PATH + r'\src\database\timetable.json'
LOGGER_PATH = PATH + r'\RedemptionBot.log'

DAILY_REMINDER_TIME = '21:00'
DAILY_SCHEDULING_TIME = '00:00'
