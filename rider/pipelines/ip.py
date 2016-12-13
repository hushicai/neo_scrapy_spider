#!/usr/bin/env python
# encoding: utf-8


import logging
import requests
import json
from urlparse import urljoin
import time
from rider.utilities.decorators import check_spider_pipeline
from rider.utilities.dbpool import createPool
from hashlib import md5
from rider.config import TEST_PROXY_URL

logger = logging.getLogger('IpPipeline')

class IpPipeline(object):

  def __init__(self):
    # 获取本机外网ip
    self.my_ip = self._get_my_ip()

    logger.info('my ip is: %s', self.my_ip)

  def open_spider(self, spider):
    self.dbpool = createPool('db_ip')

  def close_spider(self, spider):
    self.dbpool.close()

  @check_spider_pipeline
  def process_item(self, item, spider):
    ip = item['ip']
    port = item['port']
    proxies = {
      'http': 'http://%s:%s' % (ip, port),
      'https': 'https://%s:%s' % (ip, port)
    }
    t = self._get_anonymity(proxies)

    item['anonymity'] = t

    # 无效代理直接返回
    if t == 3:
      logger.info('ignore invalid ip, %s:%s', ip, port)
      return item

    # 否则入库

    fd = md5()
    fd.update(ip + ':' + port)
    item['uid'] = fd.hexdigest()

    s = self._get_speed(proxies)
    item['speed'] = s

    deferred = self.dbpool.runInteraction(self._do_interaction, item, spider)
    deferred.addCallback(self._handle_success)
    deferred.addErrback(self._handle_error, item, spider)

    return deferred

  def _do_interaction(self, transaction, item, spider):
    sql = """insert into db_ip.tb_ip_info(uid,ip,port,anonymity,speed)
    values(%s,%s,%s,%s,%s)
    """
    logger.info('insert ip %s:%s', item['ip'], item['port'])
    transaction.execute(
      sql,
      (item['uid'], item['ip'],item['port'],item['anonymity'],item['speed'])
    )
    return item

  def _handle_success(self, item):
    logger.info('adbapi runInteraction success: %s:%s', item['ip'], item['port'])

    return item

  def _handle_error(self, failure, item, spider):
    logger.error('adbapi runInteraction fail: %s', failure)

    return item

  def _get_anonymity(self, proxies):
    '''代理: 0 高匿，1 匿名，2 透明 3 无效代理'''

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
