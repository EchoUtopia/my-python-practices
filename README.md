# my-python-practices
  simplemultithreadsCrawler.py:
  
    一个简单的多线程生产者消费者爬虫，实际使用的时候可以重写parser的parse_links方法，来写自己的解析规则，
    然后将解析后将继续要爬的地址放入url队列，生产者会自动爬
    
  
  sync-flood.py：
  
    利用scapy构造包sync包，具有统计pps的功能，但是性能较差，而且scapy会响应服务器ack包
    
  watch_sync.py：
  
    监听本地目录，当目录下的文件被更改、删除、新增时，远端目录下的文件会相应被更改、删除、新增
    使用的pyinotify模块监听目录，paramkio上传文件到远端
    当变成守护进程时，将标准输出重定向到文件不起作用，不知道定向到哪去了，求大神帮忙看看
    
  my_mutex.py:
  
    使用ｒｅｄｉｓ实现一个锁，但是实际使用的时候会出现多个进程同时获得锁，
    我自己感觉是setnx不是原子的，但是没找到相应说明。望大神指点
    
  find_tail_lines.py:
    
    实现读取打印文件末尾倒数N行开始Ｍ行内容
    



trie.js:
>js实现的一个前缀树，性能强悍，不知道这归功于前缀树还是js哈哈。可以用来统计词频、单词查询、前缀匹配。
