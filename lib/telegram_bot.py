#!/usr/bin/env python
# coding: utf-8

import sys
import logging

import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

import bot_func
from bot_token import *

sys.path.append('../src')
import req_huobi

log_conf = {
    'stream': sys.stderr,
    'level': logging.INFO,
    'format': "%(asctime)s %(levelname)s %(filename)s %(threadName)s %(message)s",
    'datefmt': "%Y-%m-%d %H:%M:%S",
}
log_file = None
if log_file:
    log_conf["filename"] = log_file

logging.basicConfig(**log_conf)


bot = telegram.Bot(token=my_token)
updater = Updater(token=my_token)
dispatcher = updater.dispatcher

def command(handler,cmd=None,**kw):
    def decorater(func):
        def wrapper(*args,**kw):
            return func(*args,**kw)
        if cmd==None:
            func_hander=handler(func,**kw)
        else:
            func_hander=handler(cmd,func,**kw)
        dispatcher.add_handler(func_hander)
        return wrapper
    return decorater

@command(CommandHandler,'start')
def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='I\'am a bot belong with young, please talk to me.')

@command(CommandHandler, 'p')
def price(bot, update):
    # req_huobi.main()
    bot.sendMessage(chat_id=update.message.chat_id, text="Yes i will give you usdt price.")


@command(MessageHandler, Filters.text)
def reply_text(bot, update):
    msg = update.message.text
    msg_utf8 = msg.encode('utf-8')
    if bot_func.check_sb(msg_utf8):
        bot.sendMessage(chat_id=update.message.chat_id, text='test')
    else:
        # bot.sendMessage(chat_id=update.message.chat_id, text='test.')
        pass


@command(MessageHandler, Filters.command)
def unknown(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


# updater.start_polling()
