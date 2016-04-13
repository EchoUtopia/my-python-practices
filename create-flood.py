import os
import sys
import fcntl
import math
import json
from optparse import OptionParser
from scapy.all import *


'''
利用包回放工具来打流，通过参数 pps来控制速率
s来制定打流时间，f制定包文件，i用于制定网卡，如果不指定，则脚本自己分配
先分配没有使用的网卡，一个网卡最多可以两个人同时使用（多少人可以自己改一下），如果超过则不允许使用
'''
def get_argument():
    usage = "usage: %prog [options] arg1 arg2,using -h or --help for help"
    parser = OptionParser(usage=usage)
    parser.add_option("-p","--pps",dest="pps",help="pps of sending packets,default=1000",type="int",default=1000)
    parser.add_option("-s","--seconds",dest="seconds",\
                      help="seconds packet transmission last,default is 60 seconds",type="int",default=60)
    parser.add_option("-f","--file",dest="filename",help="the pcap file to send packets")
    parser.add_option("-i","--interface",dest="interface",\
                      help="specifing the interface,if not spcified,it will be automactic specified")
    (options, args) = parser.parse_args()
    arguments = options.__dict__
    if arguments['filename'] == None:
        parser.print_help()
        sys.exit(1)
    return arguments


def tran_time_to_loop(pps,seconds,filename):
    try:
        cap = open(filename,"rb")
    except:
        print "cannot open cap file"
        sys.exit(1)
    capfile = sniff(offline=filename)
    packet_nums = len(capfile)#获取包文件数量
    print "%s pps" % pps
    print "%s packets in capfile" % packet_nums
    loop = int(math.ceil(pps*seconds/packet_nums))#通过包文件数量、时间和pps确定回放多少次
    print "%s loops" % loop
    return loop

class flood_manage:

    # def __new__(cls, *args, **kw):
    #     if not hasattr(cls, '_instance'):
    #         orig = super(flood_manage, cls)
    #         cls._instance = orig.__new__(cls, *args, **kw)
    #     return cls._instance

    def __init__(self,inter_file="/tmp/inter_file"):
        self.__all_inter = set()
        self.__inter_file = inter_file
        self.__used_inter = self.__read_file()
        self.__get_inter_name()
        if not os.path.exists(self.__inter_file):
            os.path.touch(self.__inter_file)

    def __write_file(self,object):
        '''
        读文件时加共享锁，写文件时加排它锁
        '''
        inter_file = open(self.__inter_file,"w")
        fcntl.flock(inter_file,fcntl.LOCK_EX)
        json.dump(object,inter_file)
        fcntl.flock(inter_file,fcntl.LOCK_UN)
        inter_file.close()

    def __read_file(self):
        inter_file = open(self.__inter_file,"r")
        fcntl.flock(inter_file,fcntl.LOCK_SH)
        try:
            data = json.load(inter_file)
        except ValueError:
            data = {}
        fcntl.flock(inter_file,fcntl.LOCK_UN)
        inter_file.close()
        return data

    def __get_inter_name(self):
        '''
        获取所有非环路接口，并存如__all_inter中
        '''
        proc_net_dev = "/proc/net/dev"
        with open(proc_net_dev,"r") as f:
            f.next()
            f.next()
            for line in f:
                eth_name = line.split(":")[0].strip()
                if eth_name and eth_name != "lo":
                    self.__all_inter.add(eth_name)

    def find_aval_inter(self):
        '''
        为用户分配一个可用的接口，优先寻找没有使用的接口
        '''
        for i in self.__all_inter:
            if self.__used_inter.get(i) in (0,None):
                self.__used_inter[i] = 1
                self.__write_file(self.__used_inter)
                return i
        for i in self.__all_inter:
            if self.__used_inter.get(i) == 1:
                self.__used_inter[i] = 2
                self.__write_file(self.__used_inter)
                return i
        print "no available interface,please wait"
        sys.exit(1)


    def create_flood(self,pps,loop,filename,interface):
        '''
        打流，打完流或者出现异常（比如用户ctr+c）更新网卡使用情况：__used_inter
        因为system函数通过fork来执行代码，所以多个用户使用时不会冲突
        '''
        execStr = "tcpreplay --pps=%s --loop=%s --intf1=%s %s" % (pps,loop,interface,filename)
        try:
            os.system(execStr)
        except:
            pass
        finally:
            self.__used_inter = self.__read_file()#先更新used_inter，因为可能有其他用户使用，再在更新完的基础上将对应的接口数量减一
            self.__used_inter[interface] -= 1
            self.__write_file(self.__used_inter)


if __name__ == "__main__":
    arguments = get_argument()
    manage = flood_manage()
    interface = arguments.get("interface") or manage.find_aval_inter()
    loop = tran_time_to_loop(arguments['pps'],arguments['seconds'],arguments['filename'])
    manage.create_flood(arguments['pps'],loop,arguments['filename'],interface)


