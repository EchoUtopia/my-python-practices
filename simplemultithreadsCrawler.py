#coding=utf-8
import threading
import Queue
import urlparse
import logging
import requests
import time
import signal
import re
# from collection import nametuple

LOGGER = logging.getLogger(__name__)

def is_redirect(response):
    return response.status_code in (300, 301, 302, 303, 307)

class Crawler(threading.Thread):
    
    def __init__(self,url_queue,response_queue,
                      max_redirects=10,
                      max_tries=3,proxy=None,
                      delay_access_time=1):

        threading.Thread.__init__(self)
        self.max_redirects = max_redirects
        self.max_tries = max_tries
        self.delay_access_time = delay_access_time
        self.url_queue = url_queue
        self.response_queue = response_queue
        self.seen_urls = set()
        self.proxy = proxy
        self.session = requests.Session()
        self.session.headers.update({"User-Agent":\
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36"})

    def add_url(self, url, max_redirects=None):
        max_redirects = max_redirects != None and max_redirects or self.max_redirects
        self.url_queue.put((url,max_redirects))


    def run(self, max_redirects=None):
        max_redirects = max_redirects != None and max_redirects or self.max_redirects
        while True:
            url = self.url_queue.get(True)
            if url == None:
                break
            tries = 0
            while tries < self.max_tries:
                try:
                    if self.proxy:
                        response = self.session.get(url,proxies=self.proxy)
                    else:
                        response = self.session.get(url,proxies=self.proxy)
                    if tries > 1:
                        LOGGER.info("try %s for %s success",tries,url)
                    break
                except Exception as e:
                    LOGGER.error("try %s for %s raised %r",tries, url, e)
                tries += 1
                time.sleep(self.delay_access_time)

            else:
                LOGGER.error('%r failed after %r tries',url, self.max_tries)

            if is_redirect(response):
                location = response.headers['location']
                location_url = urlparse.urljoin(url,location)
                if max_redirects > 0:
                    self.add_url(location_url, max_redirects-1)

            else:
                print "response_url:",response.url
                response_queue.put(response)
            self.url_queue.task_done()
            time.sleep(self.delay_access_time)
        else:
            self.session.close()

class Parser(threading.Thread):
    def __init__(self,url_queue,response_queue):
        self.response_queue = response_queue
        self.url_queue = url_queue
        threading.Thread.__init__(self)
        # self.save_queue = save_queue

    def run(self):
        while True:

            response = self.response_queue.get(True)
            print response.url,type(response)
            self.response_queue.task_done()
            parse_result = self.parse_links(response)
            if parse_result == False:
                self.url_queue.put(None)
                break

    def parse_links(self, response):
        result = re.search(r'''(?i)href=["']([^\s]+)[\s"'\s]>下一页''', response._content)
        # print result.group(1)
        if result:
            url = urlparse.urljoin(response.url,result.group(1))
            self.url_queue.put(url)
            return True
        else:
            return False


if __name__ == "__main__":
    url_queue = Queue.Queue()
    url_queue.put("http://blog.csdn.net/ECHOutopia/article/list/1")
    response_queue = Queue.Queue()
    crawler = Crawler(url_queue,response_queue)
    parser = Parser(url_queue,response_queue)
    crawler.start()
    parser.start()
    crawler.join()
    parser.join()