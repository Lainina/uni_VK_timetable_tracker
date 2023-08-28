import logging
from config import LOGGER_PATH

DEBUG = False

LOGGER_LEVEL = logging.INFO

logger = logging.getLogger(__name__)

if DEBUG:
    logging.basicConfig(filename=LOGGER_PATH,
                        encoding='utf-8',
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(filename=LOGGER_PATH,
                        encoding='utf-8',
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
