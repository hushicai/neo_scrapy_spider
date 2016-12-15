#!/usr/bin/env python
# encoding: utf-8


import sys
import logging

def set_up_logger():
  """set up logger"""
  logging.basicConfig(
    stream = sys.stdout,
    level = logging.INFO,
    datefmt = '%Y-%m-%d %H:%M:%S',
    format = '%(asctime)s - [%(name)s] - %(levelname)s: %(message)s'
  )
