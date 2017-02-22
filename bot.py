#! coding: utf-8
import re
import time

import telebot
from telebot import types

from pymongo import MongoClient
from bson.objectid import ObjectId
from bunch import Bunch as bunch
from bunch import unbunchify as unbunch
from decimal import *

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import settings

from utuls import *

import btcrpc
import base64


PROCESS_STEPS = False

bot = telebot.TeleBot(settings.TG_API_TOKEN)
db = MongoClient().coinerbot


def do_start():
    try:
        user = bunch(db.account.find_one({'tg_id': message.from_user.id,}))
    except Exception as e:
        msg = bot.send_message(user.tg_id, """\
Do /start
""", parse_mode="HTML")
        return


@bot.message_handler(commands=['help',])
def help(message):
    do_start(message)

    msg = bot.send_message(user.tg_id, """\
Command list:
{}
""".format(settings.COMMANDS), parse_mode="HTML")


@bot.message_handler(commands=['send',])
def send(message):
    do_start(message)

    msg = bot.send_message(user.tg_id, """\
How much you want to send?
""", parse_mode="HTML")

    PROCESS_STEPS = True
    bot.register_next_step_handler(msg, process_send_step1)

def process_send_step1(message):
    do_start(message)

    try:
        chat_id = message.chat.id
        amount = message.text

        if re.match("^\d+?\.\d+?$", amount) is None:
            msg = bot.reply_to(message, 'Amount should be a <b>number or float</b>. \nHow much you want to send?', parse_mode="HTML")
            bot.register_next_step_handler(msg, process_send_step1)
            return 

        msg = bot.send_message(user.tg_id, """\
Write bitcoin-address to send.
""", parse_mode="HTML")

        bot.register_next_step_handler(msg, process_send_step2)
    except Exception as e:
        bot.reply_to(message, 'Oooops: '+str(e))

def process_send_step2(message):
    do_start(message)
        
    try:
        chat_id = message.chat.id
        bitcoin_address = message.text

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Cancel', 'Confirm')
        msg = bot.send_message(user.tg_id,  """\
Confirm that you want to send <b>{}</b> BTC to <b>{}</b>.
""".format(0, bitcoin_address), parse_mode="HTML", reply_markup=markup)
        bot.register_next_step_handler(msg, process_send_step3)

    except Exception as e:
        bot.reply_to(message, 'Oooops: '+str(e))
    
def process_send_step3(message):
    do_start(message)

    try:
        if message.text == 'Confirm':
            result = 'Bitcoins <b>successfully sent.</b>'
        else:
            result = '<b>Canceled!</b>'

        msg = bot.send_message(user.tg_id, result, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, 'Oooops: '+str(e))

    PROCESS_STEPS = False


@bot.message_handler(commands=['history',])
def history(message):
    do_start(message)

    msg = bot.send_message(user.tg_id, """\
History part.
""", parse_mode="HTML")


@bot.message_handler(commands=['address',])
def address(message):
    do_start(message)

    bot.send_photo(user.tg_id, generate_qrcode(address.address), caption=address.address)


@bot.message_handler(commands=['balance',])
def balance(message):
    do_start(message)

    balance = Decimal(user.bitcoin)
    msg = bot.send_message(user.tg_id, """\
Account balance: <b>{}</b> BTC
""".format(balance), parse_mode="HTML")


@bot.message_handler(commands=['start',])
def send_welcome(message):
    user_exist = False
    try:
        user = bunch(db.account.find_one({'tg_id': message.from_user.id,}))
        address = bunch(db.address.find_one({'tg_id': message.from_user.id, 'main': True}))
        user_exist = True
    except Exception as e:
        # create user if not exist
        user = bunch({})
        user.tg_id = message.from_user.id
        user.last_txn_count = 0
        user.bitcoin = 0
        user.username = message.from_user.username
        user.first_name = message.from_user.first_name
        user.last_name = message.from_user.last_name
        user._id = db.account.insert(user)

        # create user main address if not exist
        address = bunch({})
        address.tg_id = user.tg_id
        address.address = btcrpc.getnewaddress(str(user.tg_id))
        # address.address = '#bitcoin-address#'
        address.main = True
        address.recived = 0
        address.title = 'Main address'
        address._id = db.address.insert(address)

    username = 'there'

    if user.last_name or user.first_name:
        username = (user.first_name + ' ' + user.last_name).strip()
    elif user.username:
        username = user.username

    i_am = 'I am Coiner bot.'
    your_address = 'Your new bitcoin address is '

    if user_exist:
        i_am = 'Good to see you again. ;-)'
        your_address = 'Your main bitcoin-address is'

    msg = bot.send_message(user.tg_id, """\
Hi <b>{}</b>! {}
{} <b>{}</b>,
and this is your command list:
{}
""".format(username, i_am, your_address, address.address, settings.COMMANDS), parse_mode="HTML")

# @bot.message_handler(commands=['clear',])
# def clear(message):
#     if message.from_user.id in settings.ADMIN_IDS:
#         db.account.remove()
#         db.address.remove()
#         msg = bot.send_message(message.from_user.id, 'Done!', parse_mode="HTML")

bot.polling()