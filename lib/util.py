#!/usr/bin/env python
# coding: utf-8

import os
import sys

import json
import math
import heapq
import time
import datetime
import hashlib
import random
import struct
import inspect
import re
import ConfigParser
import urlparse

class DateHour( object ):
    def __init__( self ):
        self.datetime = datetime.datetime.today()

    def __str__( self ):
        return '%s - %s' %self.get_date_hour()

    def set_date_hour( self, year, month, day, hour=0, minute=0, second=0 ):
        self.datetime = datetime.datetime(year, month, day, hour, minute, second)

    def shift( self, days=0, hours=0 ):
        _days = days
        _seconds = 60*60*hours
        self.datetime = self.datetime + datetime.timedelta(days=_days, seconds=_seconds)

    def get_date_hour( self, days=0, hours=0 ):
        """like: 20121230 09
        """
        _days = days
        _seconds = 60*60*hours
        _datetime = self.datetime + datetime.timedelta(days=_days, seconds=_seconds)

        date = '%.4d%.2d%.2d' %(_datetime.year, _datetime.month, _datetime.day)
        time = '%.2d%.2d' %(_datetime.hour, _datetime.minute)
        return (date, time)

def get_cur_date():

    tmp_obj = DateHour()
    cur_date, cur_time = tmp_obj.get_date_hour()
    return cur_date


def readconffile(confpath, confilename):
    conffile = os.path.join(confpath, confilename)
    cf = myconf()
    cf.read(conffile)
    return cf


def readkv(f):
    keylendata = f.read(4)
    if len(keylendata) != 4:
        print >> sys.stderr, 'reach kv end'
        return None
    else:
        keylen = struct.unpack('I', keylendata)[0]
        if keylen > 5000:
            raise Exception('wrong key len' + str(keylen))
        key = f.read(keylen)
        valuelen = struct.unpack('I', f.read(4))[0]
        value = f.read(valuelen)
        return (
         key, value)


def writekv(f, k, v, flush=True):
    print >> sys.stderr, 'key: %s, keylen: %d, valuelen: %d' % (k, len(k), len(v))
    f.write(struct.pack('I', len(k)))
    f.write(k)
    f.write(struct.pack('I', len(v)))
    f.write(v)
    if flush:
        f.flush()

def readline(f):
    line = f.readline().strip('\r\n')
    if not line:
        log_write('WARNING', 'read line end')
        return None
    return line

def writeline(f, line, flush=True):
    f.write(line + '\n')
    if flush:
        f.flush()

def input_lines(file=sys.stdin):
    for line in file:
        yield line.strip('\r\n')


def dict2json(dict, _encoding='utf-8'):
    text = ''
    try:
        text = json.dumps(dict, ensure_ascii=False)
        if _encoding:
            text = text.encode(_encoding)
    except Exception, e:
        print >> sys.stderr, 'in dict2json:', e
    return text

def json2dict(text, _encoding='utf-8'):
    dict = None
    try: dict = json.loads(text, encoding=_encoding)
    except Exception, e: print >> sys.stderr, 'in json2dict:', e
    return dict
    return return_list

def log_write(level, str):
    frame, file_name, line_no, function_name, unknown1, unknown2 = inspect.stack()[1]
    begin = file_name.rfind('/')
    if (-1 != begin):
        file_name = file_name[begin+1:]

    time_str = time.strftime('%m/%d %H:%M:%S',time.localtime(time.time()))

    buf = '[%s][%s][%s %s() %s] %s' %(level, time_str, file_name, function_name, line_no, str)
    print >> sys.stderr, buf

def extract_site(url):
    
    url_splited = urlparse.urlsplit(url)
    site = url_splited.netloc.split(':')[0]
    return site

def run_cmd(cmd):
    log_write('NOTICE', cmd)
    ret = os.system(cmd)
    if ret != 0:
        log_write('FATAL', '{0} fail.'.format(cmd))
    return ret

common_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'}


if __name__ == '__main__':

    print 'this is util.py for common function wrote by huangyang04.'
    datehour = DateHour()
    print datehour.get_date_hour()
