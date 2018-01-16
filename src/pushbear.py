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
        logging.fatal('Exception_type: [%s] Exception: %s' %(type(e), e))
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
        try:
            req_url = '%s?sendkey=%s&text=%s&desp=%s' %(self.push_api, self.key, text, desp)
            response = urllib2.urlopen(req_url).read().strip()
        except Exception, e:
            logging.fatal('Exception_type: [%s] Exception: %s' %(type(e), e))

        ret_dict = json2dict(response)
        if not ret_dict:
            return False
        code = ret_dict.get('code', -1)
        if code != 0:
            return False
        return True

