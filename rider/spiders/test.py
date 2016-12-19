#!/usr/bin/env python
# encoding: utf-8

import scrapy

class TestSpider(scrapy.Spider):

  """测试"""

  name = 'test'

  def start_requests(self):
    start_urls = ['http://202.5.20.124:8825/dumpHeaders']

    for url in start_urls:
      yield scrapy.Request(url = url, callback = self.parse)

  def parse(self, response):
    pass
