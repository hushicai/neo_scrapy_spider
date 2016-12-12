
#!/usr/bin/env python
# encoding: utf-8


from qiniu import Auth, put_data
import requests as req
import logging

class Qiniu(object):

  """qiniu"""

  access_key = 'K49VrpZviryj_h5Gjon-hCtWCCgMBrnzyk_XhcJG'
  secret_key = 'vQT5WleVxgnv0IID9Z3XWgN9NeNT9BAbPcEAIdgj'
  bucket_name = 'assets'
  domain = 'http://ohrg9283l.bkt.clouddn.com'

  def __init__(self):
    self.q = Auth(self.access_key, self.secret_key)


  def upload(self, url, key):
    """upload to qiniu
    """
    logging.info('upload: `%s`, key: `%s`', url, key)
    token = self.q.upload_token(self.bucket_name)
    data = req.get(url)
    ret, info = put_data(token, key, data.content, mime_type = data.headers['Content-Type'])

    if info.status_code == 200:
      logging.info("upload data to qiniu ok, key: {0}".format(key))
      return self.getUrlByKey(key)
    else:
      logging.error("upload data to qiniu error, key: {0}".format(key))
      return False

  def getUrlByKey(self, key):
    return self.domain + '/' + key
    pass
