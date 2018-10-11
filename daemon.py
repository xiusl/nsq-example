#!/usr/local/bin/python3
# coding=utf-8
# author:xsl

import sys, os, time
from signal import SIGTERM
import atexit

class Daemon:

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def _daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        os.chdir('/')
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'wb', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(so.fileno(), sys.stderr.fileno())

        atexit.register(self.delpid)
        pid = str(os.getpid())
        
        with open(self.pidfile, 'w+') as f:
            f.write('%s\n' % pid)

    def delpid(self):
        os.remove(self.pidfile)

    
    def start(self):
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = 'pidfile %s already exist.\n'
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        self._daemonize()
        self.run()

    
    def stop(self):
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = 'pidfile %s does not exist.\n'
            sys.stderr.write(message % self.pidfile)
            return 

        try:
            while True:
                os.kill(pid, SIGTERM)
                time.sleep(0.2)
        except OSError as e:
            err = str(e)
            if err.find('No such process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(1)


    def restart(self):
        self.stop()
        self.start()


    def run(self):
        f = open("/tmp/daemon-log", "w")
        while 1:
            f.write('%s\n' % time.ctime(time.time()))
            f.flush()
            time.sleep(5)

            


if __name__ == '__main__':

    daemon = Daemon('/tmp/py-daemon.pid')
#    daemon = Daemon('/dd/py-daemon.pid', stdin='/dev/stdin', stdout='/dev/stdout', stderr='/dev/stderr')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage %s start/stop/restart" % sys.argv[0])
        sys.exit(2)

