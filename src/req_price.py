#!/usr/bin/env python
# coding: utf-8

import logging
import os
import sys
import time
import urllib
import urllib2
sys.path.append('../lib')

import log
import util
import api_conf
import pushbear
import bot_token

push_obj = pushbear.pushbear_class(bot_token.my_pushbear_key)

attr_name_list = [
    'userName',
    'price',
    'minTradeLimit',
    'maxTradeLimit',
    'tradeCount',
]
history_data_path = '../data/history_data'

def retry_decorator(func):
    def wrapper(*args, **kw):
        logging.info('%s start.' %(func.__name__))
        retry_cnt = 5
        ret = False
        while retry_cnt > 0:
            try:
                ret = func(*args, **kw)
            except Exception, e:
                logging.warning('Exception_type: [%s] Exception: %s' %(type(e), e))
            if ret:
                logging.info('%s end.' %(func.__name__))
                return True
            logging.info('%s retry_cnt: %d.' %(func.__name__, 5 - retry_cnt))
            retry_cnt -= 1
        return False
    return wrapper


def req_page(req_url):
    ""
    page_content = ''
    try:
        request = urllib2.Request(req_url, headers=util.common_headers)
        page_content = urllib2.urlopen(request).read().strip()
    except Exception, e:
        logging.fatal('Exception_type: [%s] Exception: %s' %(type(e), e))
    return page_content


@retry_decorator
def get_usdt_price(data_dict, action, key_name):
    usdt_url = api_conf.usdt_api_dict[action]
    page_json = req_page(usdt_url)
    if not page_json:
        return False

    page_dict = util.json2dict(page_json)
    ret_code = page_dict.get('code', -1)
    if ret_code != 200:
        return False

    ret_data_list = page_dict.get('data', {})
    if not ret_data_list:
        return False

    price_list = []
    the_price = -1
    for (idx, user_dict) in enumerate(ret_data_list):
        obj_dict = {}
        for key in attr_name_list:
            if key not in user_dict:
                return False
            val = user_dict[key]
            obj_dict[key] = val

        if len(price_list) < 5:
            price_list.append(obj_dict)

        if idx == 0:
            the_price = user_dict['price']

    data_dict['price_%s_list' %(action)] = price_list
    data_dict['%s_price_%s' %(action, key_name)] = the_price
    return True


@retry_decorator
def get_all_price(data_dict):
    ""
    # price_buy_list, buy_price_min
    ret = get_usdt_price(data_dict, 'buy', 'min')
    if not ret:
        return False

    # price_sell_list, sell_price_max
    ret = get_usdt_price(data_dict, 'sell', 'max')
    if not ret:
        return False

    return True


def write_data2local(data_dict):
    ""
    print data_dict
    del data_dict['time_obj']
    with open(history_data_path, 'a') as f:
        f.write(util.dict2json(data_dict) + '\n')


def proc_data(data_dict):
    ""
    logging.info('proc data starting...')

    # 每小时发送价格
    send_price_per_hour(data_dict)

    # 每天8, 20点发送趋势图
    if data_dict['hour'] == '08' or data_dict['hour'] == '20':
        send_price_per_day(data_dict)
    logging.info('proc data end...')
    return


def init(data_dict):
    ""
    time_obj = util.DateHour()
    date, hour, minute = time_obj.get_date_hour()
    time_str = '%s-%s-%s' %(date, hour, minute)
    data_dict['date'] = date
    data_dict['hour'] = hour
    data_dict['minute'] = minute
    data_dict['time_obj'] = time_obj
    data_dict['time_str'] = time_str

    if not os.path.exists('../data'):
        os.mkdir('../data')

    log.init_log(log_path='../log/my_app', when='H')
    return True


def run(data_dict):
    ""
    ret = init(data_dict)
    logging.info('Init succ.')

    ret = get_all_price(data_dict)
    if not ret:
        return False

    write_data2local(data_dict)
    logging.info('All succ.')
    return True


def main():
    data_dict = {}
    ret = run(data_dict)
    if not ret:
        time_str = data_dict['time_str']
        push_obj.send_msg(time_str, 'Get price fail.')


if __name__ == '__main__':
    main()
