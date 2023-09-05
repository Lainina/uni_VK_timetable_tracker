from datetime import datetime, timedelta

from config import TIMEZONE


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


def week_type(day: datetime) -> str:
    week_number = day.isocalendar()[1]
    wk_type = 'odd' if week_number % 2 == 1 else 'even'

    return wk_type
