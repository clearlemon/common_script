#!/usr/bin/env python
# coding: utf-8

import logging
import os
import json
import sys
import time
import urllib
import urllib2

def json2dict(text, _encoding='utf-8'):
    dict = None
    try: dict = json.loads(text, encoding=_encoding)
    except Exception, e:
        logging.warning('Exception_type: [%s] Exception: %s' %(type(e), e))
    return dict

class pushbear_class(object):

    def __init__(self, my_pushbear_key):
        ""
        self.push_api = 'https://pushbear.ftqq.com/sub'
        self.key = my_pushbear_key


    def send_msg(self, text='', desp=''):
        ""

        if not text:
            return False

        response = ''
        req_url = ''
        data_dict = {
            'sendkey': self.key,
            'text': text,
            'desp': desp,
        }
        try:
            request = urllib2.Request(self.push_api, urllib.urlencode(data_dict))
            response = urllib2.urlopen(request).read().strip()
        except Exception, e:
            logging.fatal('Exception_type: [%s] Exception: [%s] req_url: [%s]' %(type(e), e, req_url))

        ret_dict = json2dict(response)
        if not ret_dict:
            return False
        code = ret_dict.get('code', -1)
        if code != 0:
            logging.fatal('Pushbear send msg fail.')
            return False
        logging.info('Pushbear send msg succ.')
        return True

