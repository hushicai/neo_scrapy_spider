# neo_scrapy_spider

neo scrapy spider

## 说明

`rider/config.py`模块主要配置了URL、mysql信息等，为了安全起见，没有提交到github，使用者需要自行新建config模块，并配置相应参数。


`rider/validators/ip.py`是一个ip校验脚本，主要用来校验并清洗库中现有ip。

## 用法

### 启动ip validator任务

启动`rider/validators/ip.py`，可以用supervisor来管理ip validator进程。

### 启动ip爬虫

启动scrap爬取ip，可以用supervisor来管理ip spider进程。

### 启动其他爬虫

其他爬虫将会使用上面的ip代理池来突破爬虫限制。
