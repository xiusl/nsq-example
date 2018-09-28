# coding=utf-8
# author:xsl

import sys
import signal
import json

from log import SLLog
import logging
from functools import wraps

from pymongo import ReadPreference
from mongoengine import connect

db = 'logdb'
host = 'mongodb://127.0.0.1:27017/logdb'
connect(alias=db, host=host,read_preference=ReadPreference.SECONDARY_PREFERRED)

NSQD_TCP_ADDRS = ['127.0.0.1:4150']

def alert_exceptions(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception("Exception: %s" % (e))

    return wrapped_func

class NsqWorker(object):
    def __init__(self, nsqd_tcp_addresses=[], lookupd_http_addresses=[], \
            process_count=10, **kwargs):

        self.nsqd_tcp_addresses = nsqd_tcp_addresses
        self.lookupd_http_addresses = lookupd_http_addresses
        self.process_count = process_count
        self.nsq_kwargs = kwargs

        self.handlers = []
        self.readers = []
        self.processes = []

    def bind(self, topic, channel=None):
        channel = channel or topic

        def inner(func):
            self.handlers.append((topic, channel, func))
            return func

        return inner

    def _start(self):
        import nsq

        for topic, channel, func in self.handlers:
            func = alert_exceptions(func)
            reader = nsq.Reader(
                topic=topic,
                channel=channel,
                message_handler=func,
                nsqd_tcp_addresses=self.nsqd_tcp_addresses,
                lookupd_http_addresses=self.lookupd_http_addresses,
                **self.nsq_kwargs
            )
            self.readers.append(reader)

        nsq.run()

    def start(self):
        import multiprocessing

        for i in range(self.process_count):
            p = multiprocessing.Process(target=self._start, name="P#%s" % i)
            p.daemon = True
            p.start()
            self.processes.append(p)

        for p in self.processes:
            p.join()

    def stop(self):
        for p in self.processes:
            p.terminate()


nsq_worker = NsqWorker(
    nsqd_tcp_addresses=NSQD_TCP_ADDRS,
    process_count=4,
    heartbeat_interval=55
)

@nsq_worker.bind('sl_log')
def process_log(msg):
    data = json.loads(msg.body.decode('utf8'))
    data = data['msg']
    SLLog.create(
        msg=str(data),
        type="log"
    )
    return True


def signal_handler(signum, frame):
    nsq_worker.stop()
    sys.exit()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    nsq_worker.start()
    
