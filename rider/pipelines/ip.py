#!/usr/bin/env python
# encoding: utf-8

import logging
from rider.utilities.decorators import check_spider_pipeline
from rider.utilities.db import createPool
from hashlib import md5
from rider.utilities.ip import getAnonymity, getSpeed
from scrapy.exceptions import DropItem

logger = logging.getLogger('IpPipeline')

class IpPipeline(object):

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
    t = getAnonymity(proxies)

    item['anonymity'] = t

    # 无效代理直接返回
    if t == 3:
      raise DropItem('%s:%s' % (item['ip'], item['port']))

    # 否则入库

    fd = md5()
    fd.update(ip + ':' + port)
    item['uid'] = fd.hexdigest()

    s = getSpeed(proxies)
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
