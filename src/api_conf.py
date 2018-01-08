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


tmp_dict = {
    "code": 200,
    "message": "成功",
    "data": {
        "coinType": [
            {
                "coinId": 1,
                "coinName": "BTC",
                "coinWebIcon": "https://static.eiijo.cn/common/images/coin-logo/btc.png",
                "coinAppIcon": "https://static.bichuang.com/upload/coinlogo/20161208_APPBTC.png"
            },
            {
                "coinId": 2,
                "coinName": "USDT",
                "coinWebIcon": "https://static.eiijo.cn/common/images/coin-logo/usdt.png",
                "coinAppIcon": "https://static.bichuang.com/upload/coinlogo/20161208_APPLTC.png"
            }
        ],
        "country": [
            {
                "code": 86,
                "value": "中国",
                "shortName": null
            }
        ],
        "pay": [
            {
                "code": 1,
                "value": "支付宝",
                "shortName": null
            },
            {
                "code": 2,
                "value": "微信",
                "shortName": null
            },
            {
                "code": 3,
                "value": "银行卡",
                "shortName": null
            },
            {
                "code": 4,
                "value": "西联",
                "shortName": null
            },
            {
                "code": 5,
                "value": "Paytm",
                "shortName": null
            }
        ],
        "currency": [
            {
                "code": 86,
                "value": "人民币",
                "shortName": "CNY"
            }
        ],
        "appeal": [
            {
                "code": 0,
                "value": "对方未付款",
                "shortName": null
            },
            {
                "code": 1,
                "value": "对方未放行",
                "shortName": null
            },
            {
                "code": 2,
                "value": "对方无应答",
                "shortName": null
            },
            {
                "code": 3,
                "value": "对方有欺诈行为",
                "shortName": null
            },
            {
                "code": 4,
                "value": "其他",
                "shortName": null
            }
        ],
        "priceRange": [
            {
                "code": 1,
                "value": "10万以上",
                "shortName": "10万以上"
            },
            {
                "code": 2,
                "value": "20万以上",
                "shortName": "30万以上"
            },
            {
                "code": 3,
                "value": "30万以上",
                "shortName": "50万以上"
            }
        ]
    },
    "success": true
}
