#!/usr/bin/env python
# coding: utf-8

import logging
import os
import random
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

def sleep_decorator(func):
    def wrapper(*args, **kw):
        logging.info('[slepp_decorator] %s start.' %(func.__name__))
        time.sleep(random.choice([0.1, 0.3, 0.7, 1]))
        ret = func(*args, **kw)
        logging.info('[slepp_decorator] %s end.' %(func.__name__))
        return ret
    return wrapper


def retry_decorator(func):
    def wrapper(*args, **kw):
        logging.info('[retry_decorator] %s start.' %(func.__name__))
        retry_cnt = 5
        ret = False
        while retry_cnt > 0:
            try:
                ret = func(*args, **kw)
            except Exception, e:
                logging.warning('Exception_type: [%s] Exception: %s' %(type(e), e))
            if ret:
                logging.info('[retry_decorator] %s end.' %(func.__name__))
                return True
            logging.info('[retry_decorator] %s retry_cnt: %d.' %(func.__name__, 5 - retry_cnt))
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


@sleep_decorator
@retry_decorator
def get_usdt_price(data_dict, action, key_name):
    ""
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

def get_otcbtc_price(data_dict):
    ""
    eos_url = 'https://otcbtc.com/sell_offers?currency=eos&fiat_currency=cny&payment_type=all'


@sleep_decorator
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


def send_price_per_hour(data_dict):
    ""
    usdt_min_buy_price = data_dict['buy_price_min']
    usdt_buy_price_list = data_dict['price_buy_list']

    usdt_max_sell_price = data_dict['sell_price_max']
    usdt_sell_price_list = data_dict['price_sell_list']

    time_str = data_dict['time_str']

    msg = '* usdt_buy_min_price: %.2f\n\n' %(usdt_min_buy_price)
    msg += '| username | price | minLimit | maxLimit | tradeLimit |\n'
    msg += '| --- | --- | --- | --- | --- |\n'
    for obj_dict in usdt_buy_price_list:
        trade_limit = int(obj_dict['tradeCount'] * obj_dict['price'])
        msg += '| %s | %s | %s | %s | %s |\n' \
                %(obj_dict['userName'].encode('utf-8'), obj_dict['price'], \
                 format(obj_dict['minTradeLimit'], ','), format(obj_dict['maxTradeLimit'], ','), \
                 format(trade_limit, ','))

    msg += '\n\n'
    msg += '* usdt_sell_max_price: %.2f\n\n' %(usdt_max_sell_price)
    msg += '| username | price | minLimit | maxLimit | tradeLimit |\n'
    msg += '| --- | --- | --- | --- | --- |\n'
    for obj_dict in usdt_sell_price_list:
        trade_limit = int(obj_dict['tradeCount'] * obj_dict['price'])
        msg += '| %s | %s | %s | %s | %s |\n' \
                %(obj_dict['userName'].encode('utf-8'), obj_dict['price'], \
                 format(obj_dict['minTradeLimit'], ','), format(obj_dict['maxTradeLimit'], ','), \
                 format(trade_limit, ','))

    ret = push_obj.send_msg(text=time_str, desp=msg)
    if not ret:
        return False

    return True


def proc_data(data_dict):
    ""
    logging.info('proc data starting...')

    # 每小时发送价格
    ret = send_price_per_hour(data_dict)
    if not ret:
        return False

    return True


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

    ret = proc_data(data_dict)
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
