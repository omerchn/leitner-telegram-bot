from datetime import datetime
from zoneinfo import ZoneInfo


time_format = "%Y-%m-%d"


def get_initial_time():
    return datetime.fromtimestamp(0).strftime(time_format)


def get_today_time():
    return datetime.now(tz=ZoneInfo("Israel")).strftime(time_format)


def get_date_from_time(time: str):
    return datetime.strptime(time, time_format)


def get_time_diff(time_start: str, time_end: str):
    date_start = get_date_from_time(time_start)
    date_end = get_date_from_time(time_end)
    delta = date_end - date_start
    return delta.days


def get_days_from_time(time: str):
    return get_time_diff(time, get_today_time())
