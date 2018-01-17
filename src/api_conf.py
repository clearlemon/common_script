#!/usr/bin/env python
# coding: utf-8

usdt_api_dict = {
    'buy': 'https://api-otc.huobi.pro/v1/otc/trade/list/public?coinId=2&tradeType=1&currentPage=1&payWay=&country=&merchant=0&online=1&range=0',
    'sell': 'https://api-otc.huobi.pro/v1/otc/trade/list/public?coinId=2&tradeType=0&currentPage=1&payWay=&country=&merchant=0&online=1&range=0',
}


btc_api_dict = {
    'buy': 'https://api-otc.huobi.pro/v1/otc/trade/list/public?coinId=1&tradeType=1&currentPage=1&payWay=&country=&merchant=0&online=1&range=0',
    'sell': 'https://api-otc.huobi.pro/v1/otc/trade/list/public?coinId=1&tradeType=0&currentPage=1&payWay=&country=&merchant=0&online=1&range=0',
}


other_api_dict = {
    'price': 'https://api-otc.huobi.pro/v1/otc/base/market/price',
    'option': 'https://api-otc.huobi.pro/v1/otc/base/select/option',
}

server_chan_api = {
    # 'pushbear': 'https://pushbear.ftqq.com/sub?sendkey={sendkey}&text={text}&desp={desp}'
    'pushbear': 'https://pushbear.ftqq.com/sub',
    'server_chan': 'https://sc.ftqq.com',
}
