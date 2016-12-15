#!/usr/bin/env python
# encoding: utf-8

if __name__ == '__main__':
  import os
  import sys

  current_dir = os.path.abspath(__file__)
  project_dir = os.path.abspath(os.path.join(
    current_dir,
    os.path.pardir,
    os.path.pardir,
    os.path.pardir
  ))
  sys.path.append(project_dir)

  from rider.env import set_up_logger
  set_up_logger()

import BaseHTTPServer
import urlparse
import urllib
import json
from rider.config import API_SERVER_PORT
from rider.utilities.tools import get_logger
from rider.utilities.db import DB

logger = get_logger('rider.api.server')

class WebRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

  """请求处理类"""

  # /?action=delete&ip=xx.xx.xx.xx&port=xxxx
  # /?action=select&count=5&anonymity=1
  def do_GET(self):
    logger.info('Api server get `%s`', self.path)
    parsed_path = urlparse.urlparse(self.path)
    try:
      query = urllib.unquote(parsed_path.query)
      ret = dict(urlparse.parse_qsl(query))

      action = ret.get('action')
      if action is None:
        raise Exception('action not found!')

      del ret['action']

      if action == 'select':
        self._select_ip(ret)
      elif action == 'delete':
        self._delete_ip(ret)
      else:
        raise Exception('invalid action!')
    except Exception, e:
      logger.warning("Api server failed: %s", e)
      self.send_response(404)
      self.end_headers()
      self.wfile.write('Api server failed!')
    pass

  def _select_ip(self, params):
    limit = ''
    if params.has_key('count'):
      limit = 'limit %s' % params['count']
      del params['count']
    else:
      limit = 'limit 10'

    conditions = []

    for key in params:
      conditions.append(
        key + '=' + params[key]
      )

    condition = ' and '.join(conditions)
    if condition:
      condition = 'where ' + condition
    order_by = 'order by speed DESC'
    sql = """select * from db_ip.tb_ip_info %s %s %s""" % (condition, order_by, limit)
    db = DB('db_ip')
    rows = db.query(sql)
    db.close()
    data = [{'ip': item['ip'], 'port': item['port']} for item in rows]
    data = json.dumps(data)
    self.send_response(200)
    self.end_headers()
    self.wfile.write(data)

  def _delete_ip(self, params):
    ip = params.get('ip')
    port = params.get('port')

    if ip is None or port is None:
      self.send_response(400)
      self.end_headers()
      self.wfile.write('Invalid request!')
      return

    sql = """delete from db_ip.tb_ip_info where ip = '%s' and port = %s""" % (ip, port)
    db = DB()
    ret = db.delete(sql)
    db.close()
    self.send_response(200)
    self.end_headers()
    self.wfile.write("Success delete proxy: " + ip + ":" + port)

class Server(object):

  """api server"""

  def __init__(self):
    pass

  def start(self):
    server = BaseHTTPServer.HTTPServer(('0.0.0.0', API_SERVER_PORT), WebRequestHandler)
    self.server = server
    server.serve_forever()

  def stop(self):
    self.server.server_close()

  def __del__(self):
    self.stop()

if __name__ == '__main__':
  server = Server()
  server.start()
