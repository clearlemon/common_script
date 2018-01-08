#!/usr/bin/env python
# coding: utf-8

import telegram
from telegram.ext import Updater




bot = telegram.Bot(token=my_token)
updater = Updater(token=my_token)
dispatcher = updater.dispatcher
