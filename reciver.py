#! coding: utf8
import os

from datetime import datetime, timedelta

import btcrpc

from pymongo import MongoClient
from bson.objectid import ObjectId

from bunch import Bunch as bunch
from bunch import unbunchify as unbunch

import settings
import urllib
import base64 
import time

import requests

from decimal import *


db = MongoClient().coinerbot

accounts = db.account.find()

for account in accounts:
	account = bunch(account)
	last_txn_count = 0 if not account.last_txn_count else account.last_txn_count
	listreceivedbyaddress = btcrpc.listtransactions(str(account.tg_id), 100, last_txn_count)
	for txn in listreceivedbyaddress:
		if txn['category'] == 'receive':
			last_txn_count += 1
			datetime.fromtimestamp(int(txn['timereceived']))

			transaction = bunch({})
			transaction.system = 'bitcoind'
			transaction.type = 'recive'
			transaction.reciver = account.tg_id
			transaction.amount = txn['amount']
			transaction.address = txn['address']
			transaction.create_time = datetime.fromtimestamp(int(txn['timereceived']))
			transaction.status = 0

			db.transaction.insert(transaction)

			bitcoin_address = bunch(db.address.find_one({
				'address': transaction.address,
				'tg_id': account.tg_id
			}))

			bitcoin_address.recived = Decimal(transaction.amount) + Decimal(bitcoin_address.recived)

			db.address.update({'_id': bitcoin_address._id}, bitcoin_address)
			
			account.last_txn_count = last_txn_count
			account.bitcoin =  Decimal(transaction.amount) + Decimal(account.bitcoin)
			
	db.account.update({'_id': account._id}, account)