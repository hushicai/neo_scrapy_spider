
#  enocoding: utf-8

import re
import scrapy
from urllib import urlencode
from rider.items.weixin import ArticleItem
from rider.pipelines.weixin import ArticlePipeline
from hashlib import md5

class WeixinSpider(scrapy.Spider):
  name = 'weixin'

  query = 'JavaScript'

  # 配置spider所需pipelines
  pipelines = set([
    ArticlePipeline
  ])

  def start_requests(self):
    start_urls = [
      'http://weixin.sogou.com/weixin?type=2&query=' + self.query
    ]

    for url in start_urls:
      yield scrapy.Request(url = url, callback = self.parse)

  def parse(self, response):
    """
    parse搜索列表
    """
    for item in response.xpath('//*[@class="news-list"]/li'):
      title = "".join(item.xpath('.//h3/a/node()').extract())
      abstract = "".join(item.xpath('.//p[@class="txt-info"]/node()').extract())
      #  搜狗时效性链接
      article_temp_link = item.xpath('.//h3/a/@href').extract_first()
      #  账号名
      weixin_name = item.xpath('.//div[@class="s-p"]/a/text()').extract_first()
      weixin_id = item.xpath('.//div[@class="s-p"]/a/@data-username').extract_first()

      title = self.remove_highlight_tag(title)
      abstract = self.remove_highlight_tag(abstract)

      fd = md5()
      fd.update(weixin_id + ', ')
      fd.update(title.encode('utf8'))
      uid = fd.hexdigest()

      meta = {
        'article_title': title,
        'article_abstract': abstract,
        'article_weixin_name': weixin_name,
        'article_weixin_id': weixin_id,
        'article_uid': uid
      }

      if article_temp_link is not None:
          yield scrapy.Request(
            article_temp_link,
            callback = self.parse_detail,
            meta = meta
          )

    next_page = response\
      .xpath('//div[@id="pagebar_container"]/a[@id="sogou_next"]/@href')\
      .extract_first()

    if next_page is not None:
      next_page_url = response.urljoin(next_page)
      yield scrapy.Request(next_page_url, callback = self.parse)

  def parse_detail(self, response):
    """parse文章详情"""
    meta = response.meta

    article_item = ArticleItem()

    article_item['weixin_name'] = meta['article_weixin_name']
    article_item['weixin_id'] = meta['article_weixin_id']
    article_item['title'] = meta['article_title']
    article_item['uid'] = meta['article_uid']
    article_item['abstract'] = meta['article_abstract']

    article_item['author'] = response.xpath('//*[@id="img-content"]/div[1]/em[2]/text()').extract_first()
    article_item['content'] = "".join(response.xpath('//*[@id="js_content"]/node()').extract()).strip()
    article_item['publish_time'] = response.xpath('//*[@id="img-content"]/div[1]/em[1]/text()').extract_first()

    # 提取qrcode
    qrcode = response.xpath('//script').re_first('window\.sg_qr_code\s*=\s*"([^"]*)"')
    article_item['qrcode'] = 'http://mp.weixin.qq.com' + qrcode

    article_item['query'] = self.query
    article_item['source'] = self.name

    yield article_item

  def remove_highlight_tag(self, value):
    """删除高亮标签"""
    pattern = r'<em><!--red_beg-->([^<>]*?)<!--red_end--><\/em>'
    return re.sub(pattern, '\g<1>', value)
