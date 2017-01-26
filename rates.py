#! coding: utf8
import os
import sys
import math

from datetime import datetime, timedelta

from pymongo import MongoClient
from bson.objectid import ObjectId

from bunch import Bunch as bunch
from bunch import unbunchify as unbunch

import settings 
import hashlib
import urllib.request
import json

DB = MongoClient().coinerbot

def main():
	ticker_url = 'https://btc-e.com/api/2/btc_usd/ticker'
	json_data = urllib.request.urlopen(ticker_url).read()
	
	ticker = json.loads(json_data.decode("utf-8"))
	ticker = bunch(ticker)
	ticker.source = 'btc-e.com'
	
	DB.ticker.insert(ticker)
	ticker._id = str(ticker._id)

if __name__ == '__main__':
	main()
