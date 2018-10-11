# coding=utf-8
# author:xsl

from daemon import Daemon
import sys
from utils import put_nsq
import time
class FakeDaemon(Daemon):
    
    def run(self):
        f = open("/tmp/daemon-log", "w")
        while 1:
            t = time.ctime()
            t = {"msg": str(t)}
            a = put_nsq('sl_log', t)
            time.sleep(30)



if __name__ == '__main__':
    d = FakeDaemon('/tmp/py-daemon2.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            d.start()
        elif 'stop' == sys.argv[1]:
            d.stop()
        elif 'restart' == sys.argv[1]:
            d.restart()
        else:
            print("unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage %s start/stop/restart" % sys.argv[0])
        sys.exit(2)
