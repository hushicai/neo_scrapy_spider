#!/usr/bin/env python
# encoding: utf-8

import logging
from rider.utilities.decorators import check_spider_pipeline
from rider.utilities.db import createPool
from hashlib import md5
from rider.utilities.ip import getAnonymity, getSpeed
from rider.utilities.tools import get_current_time, get_logger
from scrapy.exceptions import DropItem

logger = get_logger('rider.pipelines.ip')

class IpPipeline(object):

  def open_spider(self, spider):
    self.dbpool = createPool('db_ip')

  def close_spider(self, spider):
    self.dbpool.close()

  @check_spider_pipeline
  def process_item(self, item, spider):
    logger.info('process item: %s', item)
    ip = item['ip']
    port = item['port']
    proxies = {
      'http': 'http://%s:%s' % (ip, port),
      'https': 'https://%s:%s' % (ip, port)
    }
    t = getAnonymity(proxies)

    item['anonymity'] = t

    # 无效代理直接返回
    if t == 3:
      raise DropItem('%s:%s' % (item['ip'], item['port']))

    # 否则入库
    s = getSpeed(proxies)

    if s is None:
      s = 100

    item['speed'] = s

    fd = md5()
    fd.update(ip + ':' + port)
    item['uid'] = fd.hexdigest()

    deferred = self.dbpool.runInteraction(self._do_interaction, item, spider)
    deferred.addCallback(self._handle_success)
    deferred.addErrback(self._handle_error, item, spider)

    return deferred

  def _do_interaction(self, transaction, item, spider):
    logger.info('Try to insert item: %s', item)
    nowTime = get_current_time()
    sql = """insert into db_ip.tb_ip_info(uid,ip,port,anonymity,speed,update_time)
    values(%s,%s,%s,%s,%s,%s)
    """
    transaction.execute(
      sql,
      (item['uid'], item['ip'],item['port'],item['anonymity'],item['speed'], nowTime)
    )
    return item

  def _handle_success(self, item):
    logger.info('adbapi runInteraction success: %s:%s', item['ip'], item['port'])

    return item

  def _handle_error(self, failure, item, spider):
    logger.error('adbapi runInteraction %s fail: %s', item ,failure)

    return item
