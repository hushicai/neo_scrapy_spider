#!/usr/bin/env python
# encoding: utf-8


import re
import logging
from rider.utilities.decorators import check_spider_pipeline
from lxml import etree
import random
import requests
import json
from urlparse import urljoin

logger = logging.getLogger('IpPipeline')

try:
  from rider.url import TEST_PROXY_URL
except Exception, e:
  logger.warning('For privacy, `rider/url.py` is ignored by git')

class IpPipeline(object):

  def __init__(self):
    # 获取本机外网ip
    self.my_ip = self._get_my_ip()

    logger.info('my ip is: %s', self.my_ip)

  @classmethod
  def from_crawler(cls, crawler):
    settings = crawler.settings

    return cls()

  @check_spider_pipeline
  def process_item(self, item, spider):
    ip = item['ip']
    port = item['port']
    proxies = {
      'http': 'http://%s:%s' % (ip, port),
      'https': 'https://%s:%s' % (ip, port)
    }
    t = self._get_anonymity(proxies)

    logger.info('anonymity: %s', t)
    item['anonymity'] = t

    return item

  def _get_anonymity(self, proxies):
    '''代理: 0 高匿，1 匿名，2 透明 3 无效代理'''

    try:
      r = requests.get(
        url = TEST_PROXY_URL,
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

        if ip == self.my_ip:
          return 3
        if http_x_forwared_for is None and http_via is None:
          return 0
        if http_via != None and http_x_forwared_for.find(self.my_ip) == -1:
          return 1
        if http_via != None and http_x_forwared_for.find(self.my_ip) != -1:
          return 2
      return 3
    except Exception,e:
      logger.warning(str(e))
      return 3

  def _get_speed(self, proxies):
    pass

  def _get_my_ip(self):
    try:
      r = requests.get(
        url = urljoin(TEST_PROXY_URL, '/getIp'),
        headers = {},
        timeout = 5
      )
      d = json.loads(r.content)

      return d['ip']
    except Exception,e:
      logger.info(str(e))
      return None
