#!/usr/bin/env python
# encoding: utf-8

import os
import logging
from datetime import datetime, timedelta
from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError
from rider.utilities.tools import get_logger
from rider.utilities.db import DB

logger = get_logger('rider.middlewares.proxy')

class HttpProxyMiddleware(object):
  # 遇到这些类型的错误直接当做代理不可用处理掉, 不再传给retrymiddleware
  DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ValueError)

  def __init__(self):
    # 保存上次不用代理直接连接的时间点
    self.last_no_proxy_time = datetime.now()
    # 一定分钟数后切换回不用代理, 因为用代理影响到速度
    self.recover_interval = 30
    # 一个proxy如果没用到这个数字就被发现老是超时, 则永久移除该proxy.
    self.dump_count_threshold = 20
    # 是否在超时的情况下禁用代理
    self.invalid_proxy_when_timeout = True
    # 当有效代理小于这个数时(包括直连), 获取新的代理
    self.extend_proxy_threshold = 10
    # 初始化代理列表
    self.proxyes = [{"proxy": None, "valid": True, "count": 0}]
    # 初始时使用0号代理(即无代理)
    self.proxy_index = 0
    # 可信代理的数量
    self.fixed_proxy_count = len(self.proxyes)
    # 每隔固定时间强制抓取新代理(min)
    self.get_proxy_interval = 120
    # 一个将被设为invalid的代理如果已经成功爬取大于这个参数的页面， 将不会被invalid
    self.invalid_proxy_threshold = 100
    # 从db中获取初始代理
    self.get_proxyes_from_db()

  def is_in_proxyes(self, proxy):
    """判断指定代理是否已经存在代理列表中"""
    for p in self.proxyes:
      if proxy == p["proxy"]:
        return True
      return False

  def get_proxyes_from_db(self):
    """从ip数据库中获取代理列表"""
    logger.info("getting proxyes from db...")
    db = DB('db_ip')
    rows = db.query("""select * from tb_ip_info order by speed DESC limit 10""")
    logger.info('got proxyes: %s', rows)
    for row in rows:
      proxy = 'http://%s:%s' % (row['ip'], row['port'])
      if self.is_in_proxyes(proxy):
        continue
      self.proxyes.append(
        {
          'proxy': proxy,
          'uid': row['uid'],
          'valid': True,
          'count': 0
        }
      )
    db.close()
    # 上一次抓新代理的时间
    self.last_get_proxy_time = datetime.now()
    # 如果发现抓不到什么新的代理了, 缩小threshold
    if self.len_valid_proxy() < self.extend_proxy_threshold:
      self.extend_proxy_threshold -= 1
    logger.info('proxyes now: %s', self.proxyes)

  def delete_proxy_in_db(self, proxy):
    """从数据库中删除指定ip"""
    db = DB('db_ip')
    db.delete("""delete from tb_ip_info where uid = %s""" % proxy['uid'])
    db.close()

  def reset_proxyes(self):
    """将所有count>=指定阈值的代理重置为valid"""
    logger.info("reset proxyes to valid")
    for p in self.proxyes:
      if p["count"] >= self.dump_count_threshold:
        p["valid"] = True

  def len_valid_proxy(self):
    """返回代理列表中有效的代理数量"""
    count = 0
    for p in self.proxyes:
      if p["valid"]:
        count += 1
    return count

  def inc_proxy_index(self):
    """
    将代理列表的索引移到下一个有效代理的位置
    如果发现代理列表只有fixed_proxy_count项有效, 重置代理列表
    如果还发现已经距离上次抓代理过了指定时间, 则抓取新的代理
    """
    while True:
      self.proxy_index = (self.proxy_index + 1) % len(self.proxyes)
      if self.proxyes[self.proxy_index]["valid"]:
        break

    # 两轮没有代理的时间间隔过短， 说明出现了验证码抖动，扩展代理列表
    if self.proxy_index == 0 and datetime.now() < self.last_no_proxy_time + timedelta(minutes=2):
      logger.info("captcha thrashing")
      self.get_proxyes_from_db()

    # 如果代理列表中有效的代理不足的话重置为valid
    if self.len_valid_proxy() <= self.fixed_proxy_count or \
        self.len_valid_proxy() < self.extend_proxy_threshold:
      self.reset_proxyes()

    # 代理数量仍然不足, 抓取新的代理
    if self.len_valid_proxy() < self.extend_proxy_threshold:
      logger.info("valid proxy < threshold: %d/%d" % (self.len_valid_proxy(), self.extend_proxy_threshold))
      self.get_proxyes_from_db()

    logger.info("now using new proxy: %s" % self.proxyes[self.proxy_index]["proxy"])

    #  一定时间没更新后可能出现了在目前的代理不断循环不断验证码错误的情况, 强制抓取新代理
    if datetime.now() > self.last_get_proxy_time + timedelta(minutes=self.get_proxy_interval):
      logger.info("%d munites since last fetch" % self.get_proxy_interval)
      self.get_proxyes_from_db()

  def set_proxy(self, request):
    "设置代理"
    proxy = self.proxyes[self.proxy_index]
    if not proxy["valid"]:
      self.inc_proxy_index()
      proxy = self.proxyes[self.proxy_index]

    if self.proxy_index == 0: # 每次不用代理直接下载时更新self.last_no_proxy_time
      self.last_no_proxy_time = datetime.now()

    logger.info('set proxy: %s', proxy)

    if proxy["proxy"]:
      request.meta["proxy"] = proxy["proxy"]
    elif "proxy" in request.meta.keys():
      del request.meta["proxy"]
    request.meta["proxy_index"] = self.proxy_index
    proxy["count"] += 1

  def invalid_proxy(self, index):
    """
    将index指向的proxy设置为invalid,
    并调整当前proxy_index到下一个有效代理的位置
    """
    if index < self.fixed_proxy_count: # 可信代理永远不会设为invalid
      self.inc_proxy_index()
      return

    if not self.proxyes[index]['valid']:
      return

    logger.info("invalidate %s" % self.proxyes[index])
    self.proxys[index]['valid'] = False

    if index == self.proxy_index:
      self.inc_proxy_index()
    if self.proxyes[index]["count"] < self.dump_count_threshold:
      # 永久删除该proxy
      self.delete_proxy_in_db(self.proxys[index])

  def process_request(self, request, spider):
    if self.proxy_index > 0  and \
        datetime.now() > (self.last_no_proxy_time + timedelta(minutes=self.recover_interval)):
      logger.info("After %d minutes later, recover from using proxy" % self.recover_interval)
      self.proxy_index = 0
    # 有些代理会把请求重定向到一个莫名其妙的地址
    request.meta["dont_redirect"] = True
    # spider发现parse error, 要求更换代理
    if "change_proxy" in request.meta.keys() and request.meta["change_proxy"]:
      logger.info("change proxy request get by spider: %s"  % request)
      self.invalid_proxy(request.meta["proxy_index"])
      request.meta["change_proxy"] = False
    self.set_proxy(request)

  def process_response(self, request, response, spider):
    """
   根据status判断是否在允许的状态码中决定是否切换到下一个proxy, 或者禁用proxy
    """
    if "proxy" in request.meta.keys():
      logger.info("process response: %s %s %s" % (request.meta["proxy"], response.status, request.url))
    else:
      logger.info("process response: None %s %s" % (response.status, request.url))

    # status不是正常的200而且不在spider声明的正常爬取过程中可能出现的
    # status列表中, 则认为代理无效, 切换代理
    if response.status != 200 \
        and (not hasattr(spider, "website_possible_httpstatus_list") \
             or response.status not in spider.website_possible_httpstatus_list):
      logger.info("response status not in spider.website_possible_httpstatus_list")
      self.invalid_proxy(request.meta["proxy_index"])
      new_request = request.copy()
      new_request.dont_filter = True
      return new_request
    else:
      return response

  def process_exception(self, request, exception, spider):
    """处理由于使用代理导致的连接异常"""
    request_proxy_index = request.meta["proxy_index"]
    logger.info("%s exception: %s" % (self.proxyes[request_proxy_index]["proxy"], exception))

    if isinstance(exception, self.DONT_RETRY_ERRORS):
      # 只有当proxy_index>fixed_proxy_count-1时才进行比较, 这样能保证至少本地直连是存在的.
      if request_proxy_index > self.fixed_proxy_count - 1 and self.invalid_proxy_when_timeout:
        if self.proxyes[request_proxy_index]["count"] < self.invalid_proxy_threshold:
          self.invalid_proxy(request_proxy_index)
        elif request_proxy_index == self.proxy_index:
          # 虽然超时，但是如果之前一直很好用，也不设为invalid
          self.inc_proxy_index()
      else:
        # 简单的切换而不禁用
        if request_proxy_index == self.proxy_index:
          self.inc_proxy_index()
      new_request = request.copy()
      new_request.dont_filter = True
      return new_request
    return None
