#!/usr/bin/env python
# encoding: utf-8

import logging
import requests
import json
from urlparse import urljoin
import time
from rider.config import TEST_PROXY_URL

logger = logging.getLogger('utilities.ip');

def getAnonymity(proxies):
  """代理: 0 高匿，1 匿名，2 透明 3 无效代理"""
  my_ip = getMyIp()

  if my_ip is None:
    return 3

  try:
    r = requests.get(
      url = urljoin(TEST_PROXY_URL, '/getAnonymity'),
      timeout = 5,
      headers = {},
      proxies = proxies
    )
    d = json.loads(r.content)

    # https://imququ.com/post/x-forwarded-for-header-in-http.html

    if r.ok:
      ip = d.get('ip')
      http_x_forwared_for = d.get('x-forwarded-for')
      http_via = d.get('via')

      if ip == my_ip:
        return 3
      if http_x_forwared_for is None and http_via is None:
        return 0
      if http_via != None and http_x_forwared_for.find(my_ip) == -1:
        return 1
      if http_via != None and http_x_forwared_for.find(my_ip) != -1:
        return 2
      return 3
  except Exception,e:
    logger.warning(str(e))
    return 3

def getSpeed(proxies):
  """获取ip相应速度"""
  start = time.time()

  try:
    r = requests.get(
      url = TEST_PROXY_URL,
      headers = {},
      timeout = 10,
      proxies = proxies
    )

    if r.ok:
      speed = round(time.time() - start, 2)
      return speed
    else:
      return 100
  except Exception, e:
    return 100

# cache my ip
_my_ip = None

def getMyIp():
  """获取本机公网ip"""

  global _my_ip

  if _my_ip is not None:
    return _my_ip

  try:
    r = requests.get(
      url = urljoin(TEST_PROXY_URL, '/getIp'),
      headers = {},
      timeout = 5
    )
    d = json.loads(r.content)

    logger.info('my ip is: %s', d['ip'])

    _my_ip = d['ip']

    return _my_ip
  except Exception,e:
    logger.info(str(e))
    return None
