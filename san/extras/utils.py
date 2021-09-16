import re
import datetime
from itertools import tee


def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def convert_dt(timestamp_string, postfix=' 00:00:00'):

    if type(timestamp_string) == datetime.date:
        timestamp_string = timestamp_string.strftime('%Y-%m-%d')

    if type(timestamp_string) == datetime.datetime:
        timestamp_string = timestamp_string.strftime('%Y-%m-a%d %H:%M:%S')

    timestamp_string = timestamp_string.replace('Z', '').replace('T', ' ')
    timestamp_string = timestamp_string[:19]

    if re.match(r'\d\d\d\d-\d\d-\d\d.\d\d:\d\d:\d\d', timestamp_string):
        return timestamp_string[:10] + ' ' + timestamp_string[11:]
    elif re.match(r'\d\d\d\d-\d\d-\d\d', timestamp_string):
        return timestamp_string + postfix
    else:
        raise Exception(f"Unknown format: {timestamp_string} !")


def str_to_ts(x):
    return datetime.datetime.strptime(convert_dt(x), '%Y-%m-%d %H:%M:%S')
