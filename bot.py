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
import pyqrcode
import btcrpc
import base64

PROCESS_STEPS = False

bot = telebot.TeleBot(settings.TG_API_TOKEN)
db = MongoClient().coinerbot


def order_dic(dic):
    ordered_dic={}
    key_ls=sorted(dic.keys())
    for key in key_ls:
        ordered_dic[key]=dic[key]
    return ordered_dic

def generate_qrcode(address):
    filename = '/tmp/' + address + '.png'
    qr = pyqrcode.create(address)
    qr.png(filename, scale=5)

    return open(filename, 'rb')

command_list = {
    'help': 'command list.',
    'address': 'bitcoin-address list.',
    'balance': 'show current balance.',
    'history': 'transaction list.',
    'send': 'send coins.',
}

commands = ''
for command in order_dic(command_list):
    commands += '/' + command + ' — <i>' + command_list[command] + '</i>\n'


@bot.message_handler(commands=['help',])
def help(message):
    try:
        user = bunch(db.account.find_one({'tg_id': message.from_user.id,}))
    except Exception as e:
        msg = bot.send_message(user.tg_id, """\
Do /start
""", parse_mode="HTML")
        return

    msg = bot.send_message(user.tg_id, """\
Command list:
{}
""".format(commands), parse_mode="HTML")

@bot.message_handler(commands=['send',])
def send(message):
    try:
        user = bunch(db.account.find_one({'tg_id': message.from_user.id,}))
    except Exception as e:
        msg = bot.send_message(user.tg_id, """\
Do /start
""", parse_mode="HTML")
        return

    msg = bot.send_message(user.tg_id, """\
How much you want to send?
""", parse_mode="HTML")

    PROCESS_STEPS = True
    bot.register_next_step_handler(msg, process_send_step1)

def process_send_step1(message):
    try:
        user = bunch(db.account.find_one({'tg_id': message.from_user.id,}))
    except Exception as e:
        msg = bot.reply_to(message, """\
Do /start
""", parse_mode="HTML")
        return

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
    try:
        user = bunch(db.account.find_one({'tg_id': message.from_user.id,}))
    except Exception as e:
        msg = bot.reply_to(message, """\
Do /start
""", parse_mode="HTML")
        return
        
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
    try:
        user = bunch(db.account.find_one({'tg_id': message.from_user.id,}))
    except Exception as e:
        msg = bot.reply_to(message, """\
Do /start
""", parse_mode="HTML")
        return

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
    try:
        user = bunch(db.account.find_one({'tg_id': message.from_user.id,}))
    except Exception as e:
        msg = bot.send_message(user.tg_id, """\
Do /start
""", parse_mode="HTML")
        return

    msg = bot.send_message(user.tg_id, """\
History part.
""", parse_mode="HTML")

@bot.message_handler(commands=['address',])
def address(message):
    try:
        user = bunch(db.account.find_one({'tg_id': message.from_user.id,}))
        address = bunch(db.address.find_one({'tg_id': message.from_user.id, 'main': True}))
    except Exception as e:
        msg = bot.reply_to(message, """\
Do /start
""", parse_mode="HTML")
        return

    bot.send_photo(user.tg_id, generate_qrcode(address.address), caption=address.address)

@bot.message_handler(commands=['balance',])
def balance(message):
    try:
        user = bunch(db.account.find_one({'tg_id': message.from_user.id,}))
    except Exception as e:
        msg = bot.reply_to(message, """\
Do /start
""", parse_mode="HTML")
        return

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
""".format(username, i_am, your_address, address.address, commands), parse_mode="HTML")

@bot.message_handler(commands=['clear',])
def clear(message):
    if message.from_user.id in settings.ADMIN_IDS:
        db.account.remove()
        db.address.remove()
        msg = bot.send_message(message.from_user.id, 'Done!', parse_mode="HTML")

# @bot.message_handler(func=lambda message: True)
# def echo_message(message):
#     if not PROCESS_STEPS:
#         return help(message)

def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user
        msg = bot.reply_to(message, 'How old are you?')
        bot.register_next_step_handler(msg, process_age_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_age_step(message):
    try:
        chat_id = message.chat.id
        age = message.text
        if not age.isdigit():
            msg = bot.reply_to(message, 'Age should be a number. How old are you?')
            bot.register_next_step_handler(msg, process_age_step)
            return
        user = user_dict[chat_id]
        user.age = age
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Male', 'Female')
        msg = bot.reply_to(message, 'What is your gender', reply_markup=markup)
        bot.register_next_step_handler(msg, process_sex_step)
    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_sex_step(message):
    try:
        chat_id = message.chat.id
        sex = message.text
        user = user_dict[chat_id]
        if (sex == u'Male') or (sex == u'Female'):
            user.sex = sex
        else:
            raise Exception()
        bot.send_message(chat_id, 'Nice to meet you ' + user.name + '\n Age:' + str(user.age) + '\n Sex:' + user.sex)
    except Exception as e:
        bot.reply_to(message, 'oooops')


bot.polling()