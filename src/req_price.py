#!/usr/bin/env python
# coding: utf-8

import logging
import os
import random
import re
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
from html_parser import otcbtc_parser

push_obj = pushbear.pushbear_class(bot_token.my_pushbear_key)

huobi_api_attr_name_list = [
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
        time.sleep(random.choice([0.2, 0.5, 0.7, 1, 1.8]))
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
def get_huobi_price(data_dict, category, action):
    ""
    logging.info('Get huobi category: [%s] action: [%s] start.' %(category, action))
    req_url = api_conf.huobi_api_dict[category][action]
    page_json = req_page(req_url)
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
        for key in huobi_api_attr_name_list:
            if key not in user_dict:
                return False
            val = user_dict[key]
            obj_dict[key] = val

        if len(price_list) < 8:
            price_list.append(obj_dict)

        if idx == 0:
            the_price = user_dict['price']

    data_dict['huobi'][category][action]['price_list'] = price_list
    data_dict['huobi'][category][action]['the_price'] = the_price

    logging.info('Get huobi category: [%s] action: [%s] end.' %(category, action))
    return True


@sleep_decorator
@retry_decorator
def get_otcbtc_price(data_dict, category, action):
    ""

    logging.info('Get otcbtc category: [%s] action: [%s] start.' %(category, action))
    req_url = api_conf.otcbtc_api_dict[category][action]
    page_html = req_page(req_url)
    if not page_html:
        return False

    parser_obj = otcbtc_parser()
    parser_obj.feed(page_html)
    parser_obj.fill_data_dict(data_dict, category, action)

    logging.info('Get otcbtc category: [%s] action: [%s] end.' %(category, action))
    return True


@sleep_decorator
@retry_decorator
def get_all_price(data_dict):
    ""

    """
        data_dict = {
            'huobi': {
                'usdt':{
                },
                'btc':{
                }
            },
            'otcbtc':{
                'eos':{
                },
                'btc':{
                },
            }
        }
    """

    huobi_attr_list = [
        ['usdt', 'buy'],
        ['usdt', 'sell'],
        ['btc', 'buy'],
        ['btc', 'sell'],
    ]
    platform_name = 'huobi'
    data_dict[platform_name] = {}
    for attr_list in huobi_attr_list:
        category = attr_list[0]
        action = attr_list[1]

        if category not in data_dict[platform_name]:
            data_dict[platform_name][category] = {}
        if action not in data_dict[platform_name][category]:
            data_dict[platform_name][category][action] = {}

        ret = get_huobi_price(data_dict, category, action)
        if not ret:
            return False

    otcbtc_attr_list = [
        ['eos', 'buy'],
        ['eos', 'sell'],
        ['btc', 'buy'],
        ['btc', 'sell'],
    ]
    platform_name = 'otcbtc'
    data_dict[platform_name] = {}
    for attr_list in otcbtc_attr_list:
        category = attr_list[0]
        action = attr_list[1]

        if category not in data_dict[platform_name]:
            data_dict[platform_name][category] = {}
        if action not in data_dict[platform_name][category]:
            data_dict[platform_name][category][action] = {}

        ret = get_otcbtc_price(data_dict, category, action)
        if not ret:
            return False

    return True


def write_data2local(data_dict):
    ""
    del data_dict['time_obj']
    with open(history_data_path, 'a') as f:
        f.write(util.dict2json(data_dict) + '\n')


def check_send_condition(data_dict):

    need_send = False
    minute = data_dict['minute']
    if int(minute) < 3:
        need_send = True

    huobi_dict = data_dict['huobi']
    huobi_usdt_dict = huobi_dict['usdt']['buy']

    otcbtc_dict = data_dict['otcbtc']
    otcbtc_eos_dict = otcbtc_dict['eos']['buy']

    usdt_min_buy_price = float(huobi_usdt_dict['the_price'])
    otcbtc_eos_min_price = float(otcbtc_eos_dict['danger']['price'])

    monitor_usdt_buy_price = api_conf.monitor_price['usdt_buy_price']
    monitor_otcbtc_eos_pirce = api_conf.monitor_price['otcbtc_eos_price']

    if usdt_min_buy_price <= monitor_usdt_buy_price:
        tmp_desp = 'now_usdt_price: %.2f monitor_price: %.2f' %(usdt_min_buy_price, monitor_usdt_buy_price)
        push_obj.send_msg(text='usdt buy price is very low and buy it now.', desp=tmp_desp)
        need_send = True

    if otcbtc_eos_min_price <= monitor_otcbtc_eos_pirce:
        tmp_desp = 'now_eos_price: %.2f monitor_price: %.2f' %(otcbtc_eos_min_price, monitor_otcbtc_eos_pirce)
        push_obj.send_msg(text='otcbtc eos price is very low and buy it now.', desp=tmp_desp)
        need_send = True

    return need_send


def gen_huobi_msg(data_dict):
    ""

    huobi_attr_list = [
        ['usdt', 'buy'],
        ['usdt', 'sell'],
        ['btc', 'buy'],
        ['btc', 'sell'],
    ]

    huobi_dict = data_dict['huobi']

    def gen_markdown(category, action, key_name, this_price, this_price_list):
        this_msg = '* %s_%s_%s_price: %.2f\n\n' \
                %(category, action, key_name, float(this_price))
        this_msg += '| username | price | amount_range | tradeLimit |\n'
        this_msg += '| --- | --- | --- | --- |\n'
        for obj_dict in this_price_list:
            trade_limit = int(obj_dict['tradeCount'] * obj_dict['price'])
            this_msg += '| %s | %s | %s - %s | %s |\n' \
                %(obj_dict['userName'].encode('utf-8'), obj_dict['price'], \
                 format(obj_dict['minTradeLimit'], ','), format(obj_dict['maxTradeLimit'], ','), \
                 format(trade_limit, ','))
        this_msg += '\n\n'
        return this_msg

    msg = '### Huobi\n'
    for attr_list in huobi_attr_list:
        category = attr_list[0]
        action = attr_list[1]
        key_name = ''
        if action == 'buy':
            key_name = 'min'
        elif action == 'sell':
            key_name = 'max'

        msg += '#### %s' %(category)
        the_price = huobi_dict[category][action]['the_price']
        price_list = huobi_dict[category][action]['price_list']
        msg += gen_markdown(category, action, key_name, the_price, price_list)
    return msg


def gen_otcbtc_msg(data_dict):
    ""

    otcbtc_attr_list = [
        ['eos', 'buy'],
        ['eos', 'sell'],
        ['btc', 'buy'],
        ['btc', 'sell'],
    ]

    otcbtc_dict = data_dict['otcbtc']

    msg = '### OTCBTC\n'
    msg += '| brief | username | amount_range | price |\n'
    msg += '| --- | --- | --- | --- |\n'
    for attr_list in otcbtc_attr_list:
        category = attr_list[0]
        action = attr_list[1]
        key_name = ''
        if action == 'buy':
            key_name == 'min'
        elif action == 'sell':
            key_name == 'max'
        msg += '#### %s' %(category)
        brief = '%s_%s_price' %(category, action)
        username = otcbtc_dict[category][action]['danger']['username']
        amount_range = otcbtc_dict[category][action]['danger']['amount_range']
        price = otcbtc_dict[category][action]['danger']['price']
        msg += '| %s | %s | %s | %s |\n' \
                %(brief, username, amount_range, price)
    return msg


def send_price(data_dict):
    ""
    msg = ''
    msg += gen_huobi_msg(data_dict)

    msg += '\n\n'

    msg += gen_otcbtc_msg(data_dict)

    time_str = data_dict['time_str']
    if check_send_condition(data_dict) or True:
        print msg
        ret = push_obj.send_msg(text=time_str, desp=msg)
        if not ret:
            return False

    return True


def proc_data(data_dict):
    ""
    logging.info('proc data starting...')

    # send price info
    ret = send_price(data_dict)
    if not ret:
        return False

    return True


def init(data_dict):
    ""
    time_obj = util.DateHour()
    # 时区
    time_obj.shift(hours=13)
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
