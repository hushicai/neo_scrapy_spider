#!/usr/bin/env python
# encoding: utf-8

import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
from rider.config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD
from rider.utilities.tools import get_logger

logger = get_logger('rider.utilities.db')

def createPool(db_name):
  db_args = dict(
    host = MYSQL_HOST,
    user = MYSQL_USER,
    passwd = MYSQL_PASSWD,
    db = db_name,
    charset = 'utf8',
    cursorclass = MySQLdb.cursors.DictCursor,
    use_unicode= True,
  )
  dbpool = adbapi.ConnectionPool('MySQLdb', **db_args)

  return dbpool

class DB(object):
  """数据库连接类"""

  def __init__(self, db_name):
    self.connection = MySQLdb.connect(
      host = MYSQL_HOST,
      user = MYSQL_USER,
      passwd = MYSQL_PASSWD,
      db = db_name,
      charset = 'utf8',
      cursorclass = MySQLdb.cursors.DictCursor,
      use_unicode= True,
    )

  def execute(self, sql, callback = lambda _: _.rowcount):
    """增删改需要commit"""
    cursor = self.connection.cursor()
    logger.info('executing `%s`', sql)
    try:
      cursor.execute(sql)
      ret = callback(cursor)
      self.connection.commit()
    except Exception, e:
      import traceback
      ret = None
      traceback.print_exc()
      self.connection.rollback()
    finally:
      cursor.close()
    return ret

  def query(self, sql):
    """查询不需要commit"""
    cursor = self.connection.cursor()
    logger.info('querying `%s`', sql)
    try:
      cursor.execute(sql)
      results = cursor.fetchall()
      return results
    except Exception, e:
      results = dict()
      raise e
    finally:
      cursor.close()
    return results

  def insert(self, sql):
    return self.execute(sql, lambda _: _.lastrowid)

  def update(self, sql):
    return self.execute(sql)

  def delete(self, sql):
    return self.execute(sql)

  def close(self):
    self.connection.close()
