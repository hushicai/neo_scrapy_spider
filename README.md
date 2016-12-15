#getMyIp neo_scrapy_spider

neo scrapy spider

## usage

`rider/config.py`模块主要配置了URL、mysql信息等，为了安全起见，没有提交到github，使用者需要自行新建config模块，并配置相应参数:

```text
TEST_PROXY_URL = 'http://xxx'
// ...
```

`rider/validators/ip.py`是一个定时任务，在crontab中配置一个小时执行一次，主要用来校验、清洗库中现有ip:

```text
* */1 * * * python /path/to/rider/validators/ip.py
```
