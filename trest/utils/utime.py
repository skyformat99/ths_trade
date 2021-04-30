#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本文件命名为utime，便于和Python核心time库区别开
utime 默认时间戳为Unix时间戳
"""
import re
import pytz
import time
import datetime
import dateutil.parser
from trest.config import settings


def timestamp(precision = 0):
    """
    获取Unix时间戳，以GMT/UTC时间「1970-01-01T00:00:00.000000」为起点，到具体时间的秒数，不考虑闰秒。
    Keyword Arguments:
        precision numeric -- 返回的时间的精度，获取毫秒用 timestamp(3) (default: {0})

    Returns:
        float -- 获取的UTC时间
    """
    return time.time() * 10**precision

def dt_now(to_tz='UTC'):
    """获取当前时间，默认为UTC时间
    Returns:
        datetime.datetime -- 例如 datetime.datetime(2018, 5, 8, 3, 50, 50, 356945, tzinfo=<UTC>)
    """
    to_tz = settings.time_zone if to_tz is None else to_tz
    tz = pytz.timezone(to_tz)
    return datetime.datetime.now(tz)

def dt_to_timezone(dt, to_tz='UTC'):
    """ 把datetime时间转换成特定时间的时间
    Arguments:
        dt {datetime.datetime} -- 时间 例如 2018-02-27 02:13:02.087558+08:00
    Keyword Arguments:
        to_tz {str}
            指定的时区 (default: {'UTC'})
            PRC 中华人民共和国
    Returns:
        datetime.datetime -- 指定时区的时间 例如 2019-04-16 00:27:14+00:00
    """
    if not isinstance(dt, datetime.datetime):
        return dt
    to_tz = settings.time_zone if to_tz is None else to_tz
    tz = pytz.timezone(to_tz)
    return dt.astimezone(tz)

def ts_to_datetime(ts, to_tz='UTC'):
    """
    ts默认为Unix时间戳，而不是本地时间戳
    """
    to_tz = settings.time_zone if to_tz is None else to_tz
    dt = datetime.datetime.fromtimestamp(ts)
    return dt_to_timezone(dt, to_tz)

def ts_to_str(ts, fmt=None, to_tz='UTC'):
    """
    ts默认为Unix时间戳，而不是本地时间戳
    fmt='%Y-%m-%d %H-%M-%S %Z' '2019-04-16 07-06-24 UTC'
    fmt=None '2019-04-16 07:06:24+00:00
    """
    to_tz = settings.time_zone if to_tz is None else to_tz
    dt = ts_to_datetime(ts, to_tz)
    return str(dt) if fmt is None else dt.strftime(fmt)

def datetime_to_ts(dt, to_tz='UTC'):
    """
    datetime转换为时间戳，默认转换为Unix时间戳
    """
    to_tz = settings.time_zone if to_tz is None else to_tz
    dt2 = dt_to_timezone(dt, to_tz)
    return dt2.timestamp()

def str_to_datetime(dt_str, to_tz='UTC'):
    """字符串格式的时间转换为datetime格式的时间

    [description]

    Arguments:
        dt_str {str} -- 字符串格式的时间， 例如 2018-02-27 02:13:02.087558+08:00 or 2018-02-27
        to_tz {str}
            指定的时区 (default: {'UTC'})
            PRC 中华人民共和国
        fmt='%Y-%m-%d %H-%M-%S'
    Keyword Arguments:
        to_tz {str} -- [description] (default: {'UTC'})

    Returns:
        [datetime.datetime] -- [description]
    """
    to_tz = settings.time_zone if to_tz is None else to_tz
    tz = pytz.timezone(to_tz)
    dt = dateutil.parser.parse(dt_str)
    dt = dt.astimezone(tz)
    return dt

def str_to_timestamp(dt_str, to_tz='UTC'):
    """
    dt_str 转换为指定时区的时间戳，默认为Unix时间戳
    str_to_timestamp('2019-04-16 07:06:24')
    str_to_timestamp('2019-04-16 07:06:24 UTC')
    str_to_timestamp('2019-04-16 07:06:24UTC')
    tz_str 需要指定的UTC时区
    """
    # str-->datetime
    dt = str_to_datetime(dt_str, to_tz)
    return datetime_to_ts(dt, to_tz)

def starttime(dt=None, tz='UTC'):
    """
    昨天的开始UTC时间 starttime() - 86400
    昨天的截止UTC时间 starttime() - 1
    今天的开始UTC时间 starttime()
    今天的截止UTC时间 starttime() + 86399
    明天的开始UTC时间 starttime() + 86400
    明天的截止UTC时间 starttime() + 172799
    2019-03-01 的开始时间 starttime((2019,3,1))
    """
    if type(dt)==tuple:
        (year, month, day) = dt
    elif type(dt) == datetime.datetime:
        year = dt.year
        month = dt.month
        day = dt.day
    else:
        dt = dt_now(tz)
        year = dt.year
        month = dt.month
        day = dt.day
    # endif
    dt_str = '%d-%d-%d 00:00:00' % (year, month, day,)
    return str_to_timestamp(dt_str, tz)
