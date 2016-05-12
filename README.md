# my-python-practices
  simplemultithreadsCrawler.py:
    一个简单的多线程生产者消费者爬虫，实际使用的时候可以重写parser的解析规则，
    然后将解析后将继续要爬的地址放入url队列，生产者会自动爬
    
  
  sync-flood.py：
    利用scapy构造包sync包，具有统计pps的功能，但是性能较差，而且scapy会响应服务器ack包
    
  watch_sync.py：
    监听本地目录，当目录下的文件被更改、删除、新增时，远端目录下的文件会相应被更改、删除、新增
    使用的pyinotify模块监听目录，paramkio上传文件到远端
    当变成守护进程时，将标准输出重定向到文件不起作用，不知道定向到哪去了，求大神帮忙看看
