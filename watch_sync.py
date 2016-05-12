import sys
import os
import pyinotify
import paramiko

server = "127.0.0.1"
port = 22
username = "echo"
password = ""

class SSHConnection():

    def __new__(cls,*args,**kw):
        if not attr(cls,'_instance'):
            orig = super(SSHConnection,cls)
            cls._instance = orig.__new__(cls,*args,**kw)
        return cls._instance

    def __init__(self,server,port,username,password):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self._ssh = None

    def connection(self):
        if not self.is_connected():
            self._ssh = paramiko.SSHClient()
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._ssh.connect(self.server, self.port,
                              username = self.username, password = self.password)

        return self._ssh

    def is_connected(self):
        transport = self._ssh.get_transport() if self._ssh else None
        return transport and transport.is_active()

    def exec_command(self,command):
        self.connection().exec_command(command)

    def get_sftp(self):
        self.connection()
        return self._ssh.open_sftp()




class EventHandler(pyinotify.ProcessEvent):

    def __init__(self,local_dir,remote_dir):
        self._ssh = SSHConnection(server,port,username,password)
        self._ssh.connection()
        self._sftp = self._ssh.get_sftp()
        self.local_dir = local_dir
        self.remote_dir = remote_dir

    # def process_IN_CREATE(self,event):
    #     print "created",event.pathname
    def get_remote_path(self,local_path):
        
        local_sub_path = self.local_dir.endswith("/") and local_path[len(self.local_dir):] or local_path[len(self.local_dir)+1:]
        # print "local_sub_path",local_sub_path

        remote_path = self.remote_dir.endswith("/") and self.remote_dir+local_sub_path or self.remote_dir+"/"+local_sub_path
        # print "remote_path",remote_path

        return remote_path


    def process_IN_DELETE(self,event):
        print "deleted",event.pathname
        self.del_remote_file(self.get_remote_path(event.pathname))

    # def process_IN_MODIFY(self,event):
    #     print "modified",event.pathname

    def process_IN_CLOSE_WRITE(self,event):
        # print "close_write",event.pathname,self.get_remote_path(event.pathname)
        self.upload_to_remote(event.pathname,self.get_remote_path(event.pathname))

    def process_IN_MOVED_FROM(self,event):
        print "moved from",event.pathname
        self.del_remote_file(self.get_remote_path(event.pathname))

    def process_IN_MOVED_TO(self,event):
        print "moved to",event.pathname
        self.upload_to_remote(event.pathname,self.get_remote_path(event.pathname))

    def del_remote_file(self,file_path):
        self._ssh.exec_command("rm %s" % file_path)

    def upload_to_remote(self,local_file,remote_file):
        try:
            self._sftp.put(local_file,remote_file)
        except Exception ,e:
            print e


def make_deamon(stdin="/dev/null",stdout="/dev/null",stderr="/dev/null"):
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.stderr.write("fork failed: (%d) %s\n" %(e.errno,e.strerror))
        sys.exit(1)
        
    os.setsid()

    try:
        pid = os.fork()
        if pid >0:
            sys.exit(0)
    except OSError,e:
        sys.stderr.write("fork failed: (%d) %s\n" %(e.errno,e.strerror))
        sys.exit(1)
        
    os.chdir("/")
    os.umask(0)

    for f in sys.stdout, sys.stderr:    f.flush()
    si = open(stdin,"r")
    so = open(stdout,"a+",0)
    se = open(stderr,"a+",0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def main():
    if len(sys.argv) != 3:
        print "Usage: python watch_sync.py watched_local_dir remote_dir"
        sys.exit(1)

    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_CREATE | pyinotify.IN_DELETE | \
    pyinotify.IN_MODIFY | pyinotify.IN_CLOSE_WRITE | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO

    handler = EventHandler(sys.argv[1],sys.argv[2])
    notifier = pyinotify.Notifier(wm, handler)

    excl_lst = ['^\..*']
    excl = pyinotify.ExcludeFilter(excl_lst)
    wdd = wm.add_watch(sys.argv[1], mask, rec=True,exclude_filter=excl)

    try:
        notifier.loop()
    except pyinotify.NotifierError, err:
        print >> sys.stderr, err

if __name__ == "__main__":
    //make_deamon(stdout="/tmp/watch_file.log")
    main()
