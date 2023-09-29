from datetime import datetime, timedelta

from config import TIMEZONE

weekday_translation = {
    'Monday': 'Понедельник',
    'Tuesday': 'Вторник',
    'Wednesday': 'Среда',
    'Thursday': 'Четверг',
    'Friday': 'Пятница',
    'Saturday': 'Суббота',
    'Sunday': 'Воскресенье'
}

week_types = ('odd', 'even')


class Day:
    def __init__(self, day: datetime | tuple[str, str]):
        if type(day) == tuple:
            self.week_type, self.weekday = day
        else:
            self.week_type = week_type(day)
            self.weekday = weekday(day)
            self.formatted_time = day.strftime('%H:%M')


def today() -> Day:
    day = Day(datetime.now(TIMEZONE))
    return day


def tomorrow() -> Day:
    day = Day(datetime.now(TIMEZONE) + timedelta(days=1))
    return day


def delta_minutes(time: str, delta: int) -> str:
    new_time = (datetime.strptime(time, '%H:%M')
                + timedelta(minutes=delta)).strftime('%H:%M')

    return new_time


def week_type(day: datetime) -> str:
    week_number = day.isocalendar()[1]
    wk_type = 'odd' if week_number % 2 == 1 else 'even'

    return wk_type


def weekday(day: datetime) -> str:
    eng_weekday = day.strftime('%A')
    ru_weekday = weekday_translation[eng_weekday]

    return ru_weekday
