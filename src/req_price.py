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

history_data_path = '../data/history_data'


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

    for platform_name, platform_val in api_conf.platform_api_dict.items():
        platform_attr_list = platform_val['attr_list']
        data_dict[platform_name] = {}
        for attr_list in platform_attr_list:
            category = attr_list[0]
            action = attr_list[1]

            if category not in data_dict[platform_name]:
                data_dict[platform_name][category] = {}
            if action not in data_dict[platform_name][category]:
                data_dict[platform_name][category][action] = {}

            tool_obj = api_conf.platform_api_dict[platform_name]['tool_obj']
            ret = tool_obj.get_price(data_dict, category, action)

            if not ret:
                return False

    return True


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

    time_str = data_dict['time_str']

    if usdt_min_buy_price <= monitor_usdt_buy_price:
        tmp_desp = 'now_usdt_price: %.2f monitor_price: %.2f' %(usdt_min_buy_price, monitor_usdt_buy_price)
        push_obj.send_msg(text='usdt buy price is very low and buy it now - %s.' %(time_str), desp=tmp_desp)
        need_send = True

    if otcbtc_eos_min_price <= monitor_otcbtc_eos_pirce:
        tmp_desp = 'now_eos_price: %.2f monitor_price: %.2f' %(otcbtc_eos_min_price, monitor_otcbtc_eos_pirce)
        push_obj.send_msg(text='otcbtc eos price is very low and buy it now - %s.' %(time_str), desp=tmp_desp)
        need_send = True

    return need_send


def send_price(data_dict):
    ""
    msg = ''

    for platform_name, platform_val in api_conf.platform_api_dict.items():
        tool_obj = api_conf.platform_api_dict[platform_name]['tool_obj']
        msg += tool_obj.gen_msg(data_dict)
        msg += '\n\n'

    time_str = data_dict['time_str']
    if check_send_condition(data_dict):
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

def write_data2local(data_dict):
    ""
    del data_dict['time_obj']
    with open(history_data_path, 'a') as f:
        f.write(util.dict2json(data_dict) + '\n')


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
