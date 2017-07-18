import time
import redis
import threading
import multiprocessing
import time
import random
import sys


class Key(unicode):
    def __getitem__(self, key):
        return Key(u"%s:%s" % (self, key))


class Mutex(object):
    def __init__(self, id, timeout, ident, re=redis.StrictRedis(host='127.0.0.1', port=13379, db=4)):
        self._key = Key(id)
        self._re = re
        self._timeout = timeout
        self._ident = ident

    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.unlock()

    def lock(self):
        _lock_key = self._key['_lock:']

        re = self._re
        while True:
            result = re.set(_lock_key, self._ident, nx=True, ex=self._timeout)
            if not result:
                time.sleep(0.01)
            else:
                return


    def unlock(self):
        _lock_key = self._key['_lock:']
        pipeline = self._re.pipeline
        with pipeline() as p:
            try:
                p.watch(_lock_key)
                lock_ident = p.get(_lock_key)
                p.multi()
                if lock_ident != self._ident:
                    return
                p.delete(_lock_key)
                p.execute()
            except:
                sys.stderr.write("not deleted\n")


def test_mutex(name, thread_num):
    for i in xrange(20):
        mutex = Mutex(name, timeout=5, ident=str(thread_num))
        mutex.lock()
        sys.stderr.write(thread_num + "locked\n")
        time.sleep(0.01)
        mutex.unlock()
        sys.stderr.write(thread_num + "---unlocked\n\n")



if __name__ == "__main__":
    threads = []
    for i in range(5):
        thread = multiprocessing.Process(target=test_mutex, args=('lock', str(i)))
        thread.daemon = True
        threads.append(thread)

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()