# encoding: utf-8

import scrapy

class Item(scrapy.Item):

  "ip信息"

  ip = scrapy.Field()
  port = scrapy.Field()
  protocol = scrapy.Field()
  # 普通、高匿、透明等
  anonymity = scrapy.Field()
  speed = scrapy.Field()
  #  country = scrapy.Field()
  #  area = scrapy.Field()
