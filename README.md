# neo_scrapy_spider

neo scrapy spider

## 说明

`rider/config.py`模块主要配置了URL、mysql信息等，为了安全起见，没有提交到github，使用者需要自行新建config模块，并配置相应参数。


`rider/validators/ip.py`是一个ip校验脚本，主要用来校验并清洗库中现有ip。

`rider/api/server.py`是一个简单的服务器，提供web接口给爬虫调用，比如调用`/?action=select&count=5`，api
server返回如下ip列表，按响应速度倒叙排列：

```json
[
  {
    "ip": "196.11.63.101",
    "port": "8080"
  },
  {
    "ip": "115.183.11.158",
    "port": "9999"
  },
  {
    "ip": "120.132.6.152",
    "port": "9100"
  },
  {
    "ip": "117.79.93.39",
    "port": "8808"
  },
  {
    "ip": "101.251.199.66",
    "port": "3128"
  }
]
```

## 用法

### 启动api服务器

启动`rider/api/server.py`，可以用supervisor来管理api server进程。

### 启动校验任务

启动`rider/validators/ip.py`，可以用supervisor来管理ip validator进程。

### 启动ip爬虫

启动scrap爬取ip，可以用supervisor来管理ip spider进程。

### 启动其他爬虫

其他爬虫将会使用上面的ip代理池来突破爬虫限制。
