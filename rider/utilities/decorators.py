# encoding: utf-8

import functools
import logging

def check_spider_pipeline(process_item_method):

  @functools.wraps(process_item_method)
  def wrapper(self, item, spider):
    name = self.__class__.__name__

    if hasattr(spider, 'pipelines') == False:
      return item

    if self.__class__ in spider.pipelines:
      logging.info("using {name}".format(name = name))
      return process_item_method(self, item, spider)
    return item

  return wrapper
