import datetime
import human_readable


def format_size(num):
    return human_readable.file_size(num)


def format_time(seconds: float) -> str:
    return human_readable.precise_delta(datetime.timedelta(seconds=seconds))
