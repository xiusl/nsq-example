# coding=utf-8
# author:xsl

from flask import Flask, jsonify

import requests
import logging


from pymongo import ReadPreference
from mongoengine import connect

db = 'logdb'
host = 'mongodb://127.0.0.1:27017/logdb'
connect(alias=db, host=host,read_preference=ReadPreference.SECONDARY_PREFERRED)

app = Flask(__name__)

from log import SLLog

@app.route('/')
def index():
    return ""


NSQD_HTTP_ADDR = '127.0.0.1:4151'

def put_nsq(topic, msg, max_retries=3):
    host = NSQD_HTTP_ADDR
    retries = 0

    while retries < max_retries:
        try:
            url = 'http://%s/pub?topic=%s'% (host, topic)
            print(url)
            resp = requests.post(url, json=msg)
            if resp.status_code == 200:
                return True
        except Exception as e:
            logging.error('nsq error --> %s, %s, %s' % (topic, msg, e))

        retries += 1

    return False


import time
# def fake_log():
#     while True:
#         t = (2009, 2, 17, 17, 3, 38, 1, 48, 0)
#         t = time.mktime(t)
#         t = time.strftime("%b %d %Y %H:%M:%S", time.gmtime(t))
#         print(t)
#         put_nsq('sl_log', t)
#         time.sleep(1)

@app.route('/fake')
def fake():
    t = time.ctime()
    t = {"msg": str(t)}
    print(t)
    a = put_nsq('sl_log', t)
    if a:
        return t["msg"]
    return 'error'


@app.route('/count')
def count():
    first_read = SLLog.objects(status=SLLog.STATUS_READ).order_by('-id').first()
    if first_read:
        unread_count = SLLog.objects(id__gt=first_read.id).count()
    else:
        unread_count = SLLog.objects().count()
    res = {'count': unread_count}
    return jsonify(res)

@app.route('/list')
def unread_list():
    ls = SLLog.objects(status__gte=0)
    ll = []
    for l in ls:
        al = l.pack()
        ll.append(al)
    return jsonify(ll)


@app.route('/fix/<id>')
def fix(id):
    l = SLLog.get(id)
    l.status = 1
    l.save()
    return jsonify(l.pack())


@app.route('/unread')
def unread():
    first_read = SLLog.objects(status=SLLog.STATUS_READ).order_by('-id').first()
    ls = []
    if first_read:
        ls = SLLog.objects(id__gt=first_read.id)
    else:
        ls = SLLog.objects().count()
    
    ll = []
    for l in ls:
        al = l.pack()
        ll.append(al)
    return jsonify(ll)

from daemon import Daemon
#import subprocess
import os
@app.route('/start')
def start():
#    d = Daemon('/tmp/py-daemon.pid')
#    d.start()
    os.system("python fakelog.py start")
    return jsonify({"msg": "start"})

@app.route('/stop')
def stop():
#    d = Daemon('/tmp/py-daemon.pid')
#    d.stop()
    os.system("python fakelog.py stop")
    return jsonify({"msg": "stop"})

if __name__ == "__main__":
    app.run(debug=True)




