#!/usr/bin/env python
# encoding: utf-8

import threading
#  import time
import sys
import logging
from pytz import timezone
from datetime import datetime, timedelta

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def get_current_time(fmt = '%Y-%m-%d %H:%M:%S'):
  """ 获取当前时间 """
  utc_now = datetime.utcnow()
  utc = timezone('UTC')
  tzchina = timezone('Asia/Shanghai')
  locale_now = utc_now.replace(tzinfo = utc).astimezone(tzchina)
  if fmt:
    return locale_now.strftime(fmt)
  else:
    return locale_now

def get_logger(name):
  return logging.getLogger(name)


if __name__ == '__main__':
  now_time = get_current_time(fmt = '')
  delta_time = timedelta(days = 3)
  print now_time
  print now_time - delta_time
