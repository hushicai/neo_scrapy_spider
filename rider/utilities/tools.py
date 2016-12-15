#!/usr/bin/env python
# encoding: utf-8

import threading
import time
import sys
import logging

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def get_current_time():
  """ 获取当前时间 """
  nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
  return nowTime

def get_logger(name):
  return logging.getLogger(name)
