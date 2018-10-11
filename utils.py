# coding=utf-8
# author:xsl

import requests
import logging

NSQD_HTTP_ADDR = '127.0.0.1:4151'

def put_nsq(topic, msg, max_retries=3):
    host = NSQD_HTTP_ADDR
    retries = 0

    while retries < max_retries:
        try:
            url = 'http://%s/pub?topic=%s'% (host, topic)
#            print(url)
            resp = requests.post(url, json=msg)
            if resp.status_code == 200:
                return True
        except Exception as e:
            pass
#            logging.error('nsq error --> %s, %s, %s' % (topic, msg, e))

        retries += 1

    return False
