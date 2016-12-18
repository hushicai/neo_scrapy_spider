
import random
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from rider.utilities.tools import get_logger

logger = get_logger('rider.middlewares.useragent')

class MyUserAgentMiddleware(UserAgentMiddleware):

  """useragent middleware"""

  def __init__(self, user_agent_list = []):
    self.user_agent_list = user_agent_list

  @classmethod
  def from_crawler(cls, crawler):
    settings = crawler.settings

    return cls(settings.get('USER_AGENT_LIST'))

  def process_request(self, request, spider):
    ua = random.choice(self.user_agent_list)

    if ua:
      logger.info('using userAgent: %s', ua)
      request.headers.setdefault('User-Agent', ua)
