
#  encoding: utf-8
import MySQLdb
import MySQLdb.cursors
import logging

class MySQLStorePipeline(object):

  def open_spider(self, spider):
    self.db = MySQLdb.connect(
      'localhost',
      'root',
      '515224',
      'db_weixin'
    )

  def close_spider(self, spider):
    self.db.close()

  def process_item(self, item, spider):
    try:
      ret = self._check_account(item)

      if ret is None:
        last_row_id = self._insert_account(item)
      else:
        last_row_id = ret[0]

      item['account_id'] = last_row_id
      self._insert_or_update_article(item)

      self.db.commit()
    except Exception, e:
      logging.error('process fail: %s', e)
      self.db.rollback()

    return item

  def _check_account(self, item):
    cursor = self.db.cursor()
    sql = """select * from db_weixin.tb_weixin_account where weixin_id = %s"""

    cursor.execute(sql, (item['weixin_id'],))
    ret = cursor.fetchone()

    return ret

  def _insert_account(self, item):
    sql = """insert into db_weixin.tb_weixin_account(weixin_id,weixin_name)
    values(%s,%s)
    """
    cursor = self.db.cursor()
    cursor.execute(
      sql,
      (item['weixin_id'], item['weixin_name'])
    )
    last_row_id = cursor.last_row_id

    return last_row_id

  def _insert_or_update_article(self, item):
    pass
