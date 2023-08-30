from config import TIMEZONE
from datetime import datetime, timedelta


def today() -> datetime:
    day = datetime.now(TIMEZONE)
    return day


def tomorrow() -> datetime:
    day = datetime.now(TIMEZONE) + timedelta(days=1)
    return day


def delta_minutes(time: str, delta: int) -> str:
    new_time = (datetime.strptime(time, '%H:%M')
                + timedelta(minutes=delta)).strftime('%H:%M')

    return new_time
