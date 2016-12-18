# encoding: utf-8

import re
import scrapy
import time
from lxml import etree
from rider.items.ip import IpItem
from rider.pipelines.ip import *
from rider.utilities.tools import get_logger
from scrapy import signals

logger = get_logger('rider.spiders.ip')

class IpSpider(scrapy.Spider):

  """ip"""

  name = 'ip'

  pipelines = set([
    IpPipeline
  ])

  ip_source_list = [
    {
      'urls': ['http://m.66ip.cn/%s.html'% n for n in ['index']+range(2,12)],
      'type':'xpath',
      'pattern': ".//*[@class='profit-c']/table/tr[position()>1]",
      'postion':{'ip':'./td[1]','port':'./td[2]'}
    },
    #  {
      #  'urls': ['http://m.66ip.cn/areaindex_%s/%s.html'%(m,n) for m in range(1,35) for n in range(1,10)],
      #  'type':'xpath',
      #  'pattern': ".//*[@id='footer']/div/table/tr[position()>1]",
      #  'postion':{'ip':'./td[1]','port':'./td[2]'}
    #  },
    #  {
      #  'urls': ['http://www.kuaidaili.com/proxylist/%s/'% n for n in range(1,11)],
      #  'type': 'xpath',
      #  'pattern': ".//*[@id='index_free_list']/table/tbody/tr[position()>0]",
      #  'postion':{'ip':'./td[1]','port':'./td[2]'}
    #  },
    #  {
      #  'urls': ['http://www.kuaidaili.com/free/%s/%s/'% (m,n) for m in ['inha', 'intr', 'outha', 'outtr'] for n in range(1,11)],
      #  'type':'xpath',
      #  'pattern': ".//*[@id='list']/table/tbody/tr[position()>0]",
      #  'postion':{'ip':'./td[1]','port':'./td[2]'}
    #  },
    #  {
      #  'urls': ['http://www.cz88.net/proxy/%s'% m for m in ['index.shtml']+['http_%s.shtml' % n for n in range(2, 11)]],
      #  'type':'xpath',
      #  'pattern':".//*[@id='boxright']/div/ul/li[position()>1]",
      #  'postion':{'ip':'./div[1]','port':'./div[2]'}
    #  },
    #  {
      #  'urls': ['http://www.ip181.com/daili/%s.html'% n for n in range(1, 11)],
      #  'type':'xpath',
      #  'pattern': ".//div[@class='row']/div[3]/table/tbody/tr[position()>1]",
      #  'postion':{'ip':'./td[1]','port':'./td[2]'}
    #  },
    #  {
      #  'urls': ['http://www.xicidaili.com/%s/%s'%(m,n) for m in ['nn', 'nt', 'wn', 'wt'] for n in range(1, 8) ],
      #  'type':'xpath',
      #  'pattern': ".//*[@id='ip_list']/tr[position()>1]",
      #  'postion':{'ip':'./td[2]','port':'./td[3]'}
    #  },
    #  {
      #  'urls':['http://www.cnproxy.com/proxy%s.html'% i for i in range(1,11)],
      #  'type':'module',
      #  'moduleName':'CnproxyPraser',
      #  'pattern':r'<tr><td>(\d+\.\d+\.\d+\.\d+)<SCRIPT type=text/javascript>document.write\(\"\:\"(.+)\)</SCRIPT></td><td>(HTTP|SOCKS4)\s*',
      #  'postion':{'ip':0,'port':1}
    #  },
  ]

  @classmethod
  def from_crawler(cls, crawler, *args, **kwargs):
    crawler.signals.connect(cls.handle_start_signal, signals.engine_started)
    crawler.signals.connect(cls.handle_end_signal, signals.engine_stopped)
    crawler.signals.connect(cls.handle_idle_sinal, signals.spider_idle)

    return cls()

  def start_requests(self):
    for parser in self.ip_source_list:
      meta = {
        'ip_parser': parser
      }

      for url in parser['urls']:
        yield scrapy.Request(url = url, callback = self.parse, meta = meta)
        # 暂停3s
        time.sleep(3)

  def parse(self, response):
    logger.info('parsing `%s`', response.url)
    meta = response.meta
    parser = meta['ip_parser']

    if parser['type'] == 'xpath':
      return self.XpathPraser(response, parser)
    elif parser['type'] == 'regular':
      return self.RegularPraser(response, parser)
    elif parser['type'] == 'module':
      return getattr(self,parser['moduleName'], None)(response, parser)
    else:
      return None

  def XpathPraser(self, response, parser):
    doc = etree.HTML(response.body)
    proxys = doc.xpath(parser['pattern'])

    # print proxys
    for proxy in proxys:
      try:
        ip = proxy.xpath(parser['postion']['ip'])[0].text
        port = proxy.xpath(parser['postion']['port'])[0].text
      except Exception,e:
        logger.warning(str(e))
        continue

      ipItem = IpItem()
      ipItem['ip'] = ip
      ipItem['port'] = port
      ipItem['speed'] = 100

      yield ipItem

  def RegularPraser(self, response, parser):
    pattern = re.compile(parser['pattern'])
    matchs = pattern.findall(response.body)
    if matchs != None:
      for match in matchs:
        ip = match[parser['postion']['ip']]
        port = match[parser['postion']['port']]

        ipItem = IpItem()
        ipItem['ip'] = ip
        ipItem['port'] = port
        ipItem['speed'] = 100

        yield ipItem

  def CnproxyPraser(self, response, parser):
    proxylist = self.RegularPraser(response, parser)
    chardict ={
      'v':'3',
      'm':'4',
      'a':'2',
      'l':'9',
      'q':'0',
      'b':'5',
      'i':'7',
      'w':'6',
      'r':'8',
      'c':'1'
    }

    for item in proxylist:
      port = item['port']
      new_port = ''
      for i in range(len(port)):
        if port[i] != '+':
          new_port += chardict[port[i]]
      item['port'] = int(new_port)
      yield item

  @classmethod
  def handle_idle_sinal(self, spider):
    logger.info('--------------- spider idle -----------------')

  @classmethod
  def handle_start_signal(cls):
    logger.info('-------------- engine started ----------------')

  @classmethod
  def handle_end_signal(cls):
    logger.info('-------------- engine stoped ----------------')
