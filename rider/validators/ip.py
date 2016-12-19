#!/usr/bin/env python
# encoding: utf-8

if __name__ == '__main__':
  import os
  import sys

  current_dir = os.path.abspath(__file__)
  project_dir = os.path.abspath(os.path.join(
    current_dir,
    os.path.pardir,
    os.path.pardir,
    os.path.pardir
  ))
  sys.path.append(project_dir)

  from rider.env import set_up_logger
  set_up_logger()

import time
import datetime
from rider.utilities.db import DB
from rider.utilities.tools import set_interval, get_current_time, get_logger
from rider.utilities.ip import getSpeed

logger = get_logger('rider.validators.ip')

class IpValidator(object):

  # 1小时check一次
  CHECK_INTERVAL_TIME = 60 * 60 # 秒

  # 3天过期
  EXPIRE_MAX_DAY = 3 # 天

  def __init__(self):
    self.db = DB('db_ip')

  def run(self):
    self.check_ip()

  def check_ip(self):
    logger.info('-------- checking ip ---------')
    self.delete_expire_ip()
    self.scan_db_ip()

  def scan_db_ip(self):
    """全表扫描ip"""
    logger.info('Scan ip...')
    sql = """select * from db_ip.tb_ip_info order by update_time DESC limit 1000"""
    rows = self.db.query(sql)
    logger.info('Scanned ip counts: %s', len(rows))
    for row in rows:
      self.check_specific_ip(row)

  def delete_expire_ip(self):
    """删除过期ip"""
    logger.info('Delete expire ip....')
    now_time = get_current_time(fmt = '')
    update_time = (now_time - datetime.timedelta(days = self.EXPIRE_MAX_DAY))\
      .strftime('%Y-%m-%d %H:%M:%S')
    sql = """delete from db_ip.tb_ip_info where update_time < '%s'""" % update_time
    cnt = self.db.delete(sql)
    logger.info('Delete %s expire ip', cnt)

  def delete_specific_ip(self, item):
    """删除ip"""
    logger.info('Delete ip, %s:%s', item['ip'], item['port'])
    sql = """delete from db_ip.tb_ip_info where id = %s""" % item['id']
    self.db.delete(sql)

  def update_specific_ip(self, item):
    """更新ip"""
    logger.info('Update ip, %s:%s', item['ip'], item['port'])
    nowTime = get_current_time()
    sql = """update  db_ip.tb_ip_info set speed = %s, update_time = '%s'
    where id = %s""" % (item['speed'], nowTime, item['id'])
    self.db.update(sql)

  def check_specific_ip(self, item):
    """检测ip"""
    logger.info('Checking ip, %s:%s', item['ip'], item['port'])
    ip = item['ip']
    port = item['port']
    proxies = {
      'http': 'http://%s:%s' % (ip, port),
      'https:': 'https://%s:%s' % (ip, port)
    }
    speed = getSpeed(proxies)
    if speed is None:
      # 删除
      self.delete_specific_ip(item)
    else:
      # 更新
      item['speed'] = speed
      self.update_specific_ip(item)

  def stop(self):
    self.db.close()

  def __del__(self):
    self.stop()


if __name__ == '__main__':
  validator = IpValidator()
  while True:
    logger.info('Ip validator started --------')
    validator.run()
    logger.info('Ip validator done ---------')
    logger.info('Take a rest: %s ----------', IpValidator.CHECK_INTERVAL_TIME)
    time.sleep(IpValidator.CHECK_INTERVAL_TIME)
