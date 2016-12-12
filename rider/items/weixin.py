#  encoding: utf-8

import scrapy

class ArticleItem(scrapy.Item):

  """微信文章信息"""

  title = scrapy.Field()
  uid = scrapy.Field()
  account_id = scrapy.Field()
  abstract = scrapy.Field()
  weixin_name = scrapy.Field()
  weixin_id = scrapy.Field()
  publish_time = scrapy.Field(serilizer = str)
  content = scrapy.Field()
  author = scrapy.Field()
  qrcode = scrapy.Field()

  query = scrapy.Field()
  source = scrapy.Field()
  #  read_count = scrapy.Field()
  #  praise_count = scrapy.Field()
