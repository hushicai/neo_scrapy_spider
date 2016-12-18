# encoding: utf-8

import scrapy

class IpItem(scrapy.Item):

  "ip信息"

  uid = scrapy.Field()
  ip = scrapy.Field()
  port = scrapy.Field()
  #  protocol = scrapy.Field()
  anonymity = scrapy.Field()
  speed = scrapy.Field()
  #  country = scrapy.Field()
  #  area = scrapy.Field()
