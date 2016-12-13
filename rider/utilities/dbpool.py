
#!/usr/bin/env python
# encoding: utf-8

import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
from rider.utilities.decorators import check_spider_pipeline
from rider.config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD

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
