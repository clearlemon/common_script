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
from sgmllib import SGMLParser

def get_value_by_attr_key(tag_attrs, str_attr_k):
    ""
    str_attr_v = ''
    for k,v in tag_attrs:
        if k == str_attr_k:
            str_attr_v = v
            break
    return str_attr_v

def str_single_line(str_in):
    str_out = str_in.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
    str_out = str_out.replace('<br>', ' ').replace('<p>', ' ').replace('</p>', ' ')
    str_out = str_out.replace('<br/>', ' ').replace('<p/>', ' ')
    str_out = str_out.replace('&nbsp;', ' ').strip()
    return str_out

def str_gbk_to_utf8(str_in):
    return str_in.decode('gbk').encode('utf-8', 'ignore')

def handle_text(text, need_trans = 0):
    new_text = str_single_line(text)
    if need_trans == 1:
        return str_gbk_to_utf8(new_text)
    else:
        return new_text


class otcbtc_parser(SGMLParser):
    ""

    def __init__(self):
        SGMLParser.__init__(self)
        self.in_danger = 0
        self.username_danger = ''
        self.amount_range_danger = ''
        self.price_danger = -1

        self.in_info = 0
        self.username_info = ''
        self.amount_range_info = ''
        self.price_info = -1

        self.in_username = 0
        self.in_amount_range = 0
        self.in_price = 0


    def start_div(self, attrs):
        div_class = get_value_by_attr_key(attrs, 'class')
        if div_class == 'recommend-fixed-line recommend-fixed-line--danger':
            self.in_danger = 1
        if div_class == 'recommend-card__header recommend-card__header--info':
            self.in_info = 1
        if div_class == 'recommend-card__action':
            self.in_danger = 0
            self.in_info = 0
        if div_class == 'recommend-card__user-name':
            self.in_username = 1
        if div_class == 'recommend-card__amount-range':
            self.in_amount_range = 1
        if div_class == 'recommend-card__price':
            self.in_price = 1

    def end_div(self):
        self.in_username = 0
        self.in_amount_range = 0
        self.in_price = 0

    def start_a(self, attrs):
        self.in_username += 1

    def end_a(self):
        self.in_username = 0

    def handle_data(self, text):
        if self.in_danger > 0:
            if self.in_username > 1:
                self.username_danger = handle_text(text)
            elif self.in_amount_range > 0:
                self.amount_range_danger = handle_text(text)
            elif self.in_price > 0:
                self.price_danger = handle_text(text)
        elif self.in_info > 0:
            if self.in_username > 1:
                self.username_info = handle_text(text)
            elif self.in_amount_range > 0:
                self.amount_range_info = handle_text(text)
            elif self.in_price > 0:
                self.price_info = handle_text(text)

    def fill_data_dict(self, data_dict):
        data_dict['otcbtc'] = {}
        data_dict['otcbtc']['danger'] = {
            'username': self.username_danger,
            'amount_range': self.amount_range_danger,
            'price': self.price_danger,
        }

        data_dict['otcbtc']['info'] = {
            'username': self.username_info,
            'amount_range': self.amount_range_info,
            'price': self.price_info,
        }
        return True