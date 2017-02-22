#! coding: utf8
import os
from utils import order_dic


BASE_PATH = os.path.dirname(__file__)

ACCOUNTS_AI_START = 700000

BITCOIN_RPC = 'http://*************:***************@127.0.0.1:8332'

TG_API_TOKEN = '***********:*******************************'

ADMIN_IDS = [204107548,]

SENDER = 'noreply@mail.com'
SMTP_SERVER = 'smtp.mail.com'
SMTP_PORT = 465
SMTP_PASWORD = '**********'

COMMAND_LIST = {
    'help': 'command list.',
    'address': 'bitcoin-addres list.',
    'balance': 'show current balance.',
    'history': 'transaction list.',
    'send': 'send coins.',
}

COMMANDS = ''
for command in order_dic(COMMAND_LIST):
    COMMANDS += '/' + command + ' — <i>' + COMMAND_LIST[command] + '</i>\n'