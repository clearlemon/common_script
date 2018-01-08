#!/usr/bin/env python
# coding: utf-8

import os
import sys
import urllib
import urllib2
sys.path.append('../lib')

import util
import api_conf
import telegram_bot



def req_page(req_url):
    ""
    request = urllib2.Request(req_url, headers=util.common_headers)
    page_content = ''
    try:
        page_content = urllib2.urlopen(request).read().strip()
    except Exception, e:
        util.log_write('FATAL', e)
    return page_content


def proc_page(data_dict):
    usdt_buy_url = api_conf.usdt_api_dict['buy']
    page_json = req_page(usdt_buy_url)

    page_dict = util.json2dict(page_json)
    ret_code = page_dict.get('code', -1)
    if ret_code != 200:
        return

    ret_data_list = page_dict.get('data', {})
    if not ret_data:
        return

    price_list = []
    for (idx, user_dict) in enumerate(ret_data_list):
        user_name = user_dict.get('userName', '-1')
        price = user_dict.get('price', -1)
        min_trade_limit = user_dict.get('minTradeLimit', -1)
        max_trade_limit = user_dict.get('maxTradeLimit', -1)

        price_list.append([user_name, price, min_trade_limit, max_trade_limit])

        if idx >= 4:
            break
    data_dict['price_list'] = price_list
    return


def proc_data(data_dict)



def main():
    ""
    data_dict = {}
    proc_page(data_dict)
    proc_data(data_dict)


if __name__ == '__main__':
    main()
