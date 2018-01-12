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
import telegram_bot

attr_name_list = [
    'userName',
    'price',
    'minTradeLimit',
    'maxTradeLimit',
]

FAIL = -1
SUCC = 0
history_data_path = '../data/history_data'


def req_page(req_url):
    ""
    request = urllib2.Request(req_url, headers=util.common_headers)
    page_content = ''
    try:
        page_content = urllib2.urlopen(request).read().strip()
    except Exception, e:
        util.log_write('FATAL', e)
    return page_content


def get_page_price(data_dict):
    ""
    usdt_buy_url = api_conf.usdt_api_dict['buy']
    page_json = req_page(usdt_buy_url)

    page_dict = util.json2dict(page_json)
    ret_code = page_dict.get('code', -1)
    if ret_code != 200:
        return FAIL

    ret_data_list = page_dict.get('data', {})
    if not ret_data_list:
        return FAIL

    price_list = []
    min_price = 100000000000
    for (idx, user_dict) in enumerate(ret_data_list):
        obj_dict = {}
        for key in attr_name_list:
            if key not in user_dict:
                return FAIL
            val = user_dict[key]
            obj_dict[key] = val

        price_list.append(obj_dict)

        min_price = min(min_price, user_dict['price'])

    data_dict['price_list'] = price_list
    data_dict['min_price'] = min_price
    return SUCC


def fail_to_send_msg(data_dict, text_msg):
    ""
    msg = ''
    msg = '%s %s' %(data_dict.get('time_str', 'get time fail'), text_msg)
    telegram_bot.bot.send_message(chat_id=telegram_bot.my_channel_id, text=msg)


def gen_time_seq(data_dict):
    ""
    seq_range = 10
    if 'time_obj' not in data_dict or 'date' not in data_dict \
        or 'hour' not in data_dict:
        return FAIL
    time_obj = data_dict['time_obj']
    date = data_dict['date']
    hour = data_dict['hour']
    dates_set = set([date])
    for idx in xrange(1, seq_range):
        tmp_date, tmp_hour, tmp_time = time_obj.get_date_hour(days=-idx)
        dates_set.add(tmp_date)

    hours_set = set(['%s%s' %(date, hour)])
    for idx in xrange(1, seq_range):
        tmp_date, tmp_hour, tmp_time = time_obj.get_date_hour(hours=-idx)
        hours_set.add('%s%s' %(tmp_date, tmp_hour))
    data_dict['dates_set'] = dates_set
    data_dict['hours_set'] = hours_set
    return SUCC


def merge_history_price(data_dict):
    ""
    if not os.path.exists(history_data_path):
        logging.info('%s not exists.' %(history_data_path))
        return SUCC

    ret = gen_time_seq(data_dict)
    if ret == FAIL:
        logging.fatal('gen time seq fail.')
        return FAIL

    need_dates_set = data_dict['dates_set']
    need_hours_set = data_dict['hours_set']

    history_data_dict = {}
    for line in util.input_lines(open(history_data_path)):
        if not line:
            continue
        json_dict = util.json2dict(line)
        if not json_dict:
            continue

        if 'date' not in json_dict or 'hour' not in json_dict \
            or 'minute' not in json_dict or 'min_price' not in json_dict:
            return FAIL
        tmp_date = json_dict['date']
        tmp_hour = json_dict['hour']
        tmp_min_price = json_dict['min_price']
        if tmp_date in need_dates_set:
            history_data_dict[tmp_date] = min(history_data_dict.get(tmp_date, 100000000000), tmp_min_price)
        date_hour_time = '%s%s' %(tmp_date, tmp_hour)
        if date_hour_time in need_hours_set:
            history_data_dict[date_hour_time] = min(history_data_dict.get(date_hour_time, 100000000000), tmp_min_price)
    data_dict['history_data'] = history_data_dict
    return SUCC


def write_data2local(data_dict):
    ""
    del data_dict['time_obj']
    data_dict['dates_set'] = sorted(list(data_dict['dates_set']), key=lambda x:int(x))
    data_dict['hours_set'] = sorted(list(data_dict['hours_set']), key=lambda x:int(x))
    with open(history_data_path, 'a') as f:
        f.write(util.dict2json(data_dict) + '\n')


def proc_data(data_dict):
    ""
    price_list = data_dict.get('price_list', [])
    min_price = data_dict.get('min_price', None)
    if not price_list or not min_price:
        return FAIL


def init(data_dict):
    ""
    time_obj = util.DateHour()
    date, hour, minute = time_obj.get_date_hour()
    time_str = '%s%s%s' %(date, hour, minute)
    data_dict['date'] = date
    data_dict['hour'] = hour
    data_dict['minute'] = minute
    data_dict['time_obj'] = time_obj
    data_dict['time_str'] = time_str

    if not os.path.exists('../data'):
        os.mkdir('../data')

    log.init_log(log_path='../log/my_app', when='H')
    return


def run():
    ""
    data_dict = {}
    init(data_dict)
    logging.info('Init succ.')

    ret = SUCC
    retry_cnt = 0
    while retry_cnt < 5:
        ret = get_page_price(data_dict)
        if ret == SUCC:
            logging.info('get page price succ retry_cnt: %d.' %(retry_cnt))
            break
        retry_cnt += 1
        time.sleep(1)

    if ret == FAIL:
        fail_to_send_msg(data_dict, 'get huobi price fail.')
        return

    ret = merge_history_price(data_dict)
    if ret == FAIL:
        fail_to_send_msg(data_dict, 'merge history data fail.')
        return

    ret = proc_data(data_dict)
    if ret == FAIL:
        fail_to_send_msg(data_dict, 'proc data fail.')
        return

    write_data2local(data_dict)


def main():
    run()


if __name__ == '__main__':
    main()
