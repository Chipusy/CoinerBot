#!coding: utf8
import os
import sys
import math
import string
from datetime import datetime, timedelta

import settings
	
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
# import logging

# logging.basicConfig()
# logging.getLogger("BitcoinRPC").setLevel(logging.DEBUG)

access = AuthServiceProxy(settings.BITCOIN_RPC)

def getnewaddress(account):
	return access.getnewaddress(account)

def getbalance(account=False):
	return access.getbalance(account) if account else access.getbalance()

def getaccount(address):
	return access.getaccount(address)

def getreceivedbyaddress(address):
	return access.getreceivedbyaddress(address)

def listreceivedbyaddress(address):
	return access.listreceivedbyaddress(address, True)

def listtransactions(account, count, skip):
	return access.listtransactions(account, count, skip)

def send_to_address(address, amount):
	try:
		access.sendtoaddress(address, amount)
	except Exception as e:
		return 'error'
	return True

if __name__ == '__main__':
	print (getbalance())