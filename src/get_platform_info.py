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

import api_conf
import util
import html_parser


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


class huobi(object):

    @staticmethod
    @sleep_decorator
    @retry_decorator
    def get_price(data_dict, category, action):
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

        huobi_api_attr_name_list = [
            'userName',
            'price',
            'minTradeLimit',
            'maxTradeLimit',
            'tradeCount',
        ]

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


    @staticmethod
    def gen_msg(data_dict):
        ""
        platform_name = 'huobi'
        huobi_attr_list = api_conf.platform_api_dict[platform_name]['attr_list']

        huobi_dict = data_dict[platform_name]

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

        msg = '\n\n### Huobi\n\n'
        for attr_list in huobi_attr_list:
            category = attr_list[0]
            action = attr_list[1]
            key_name = ''
            if action == 'buy':
                key_name = 'min'
            elif action == 'sell':
                key_name = 'max'

            msg += '\n\n#### %s\n\n' %(category)
            the_price = huobi_dict[category][action]['the_price']
            price_list = huobi_dict[category][action]['price_list']
            msg += gen_markdown(category, action, key_name, the_price, price_list)
        return msg


class otcbtc(object):


    @staticmethod
    @sleep_decorator
    @retry_decorator
    def get_price(data_dict, category, action):
        ""

        logging.info('Get otcbtc category: [%s] action: [%s] start.' %(category, action))
        req_url = api_conf.otcbtc_api_dict[category][action]
        page_html = req_page(req_url)
        if not page_html:
            return False

        parser_obj = html_parser.otcbtc_parser()
        parser_obj.feed(page_html)
        parser_obj.fill_data_dict(data_dict, category, action)

        logging.info('Get otcbtc category: [%s] action: [%s] end.' %(category, action))
        return True


    @staticmethod
    def gen_msg(data_dict):
        ""
        platform_name = 'otcbtc'
        otcbtc_attr_list = api_conf.platform_api_dict[platform_name]['attr_list']

        otcbtc_dict = data_dict[platform_name]

        msg = '\n\n### OTCBTC\n\n'
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
            # msg += '\n\n#### %s\n\n' %(category)
            brief = '%s_%s_price' %(category, action)
            username = otcbtc_dict[category][action]['danger']['username']
            amount_range = otcbtc_dict[category][action]['danger']['amount_range']
            price = otcbtc_dict[category][action]['danger']['price']
            msg += '| %s | %s | %s | %s |\n' \
                    %(brief, username, amount_range, price)
        return msg

