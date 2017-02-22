Bitcoin wallet telegram bot. 

#CoinerBot is a telegram client for bitcoind. This is not stable version! Work in progress.


##Install on ubuntu/debian.

###You already must have configured bitcoins with rpc!

####First of all we will need mongo, python2.7+, pip and virtualenv, make as root:

	apt-get install python-pip python-dev build-essential mongodb
	pip install virtualenv

####Now lets clone project:

	git clone git@github.com:Chipusy/CoinerBot.git
	cd CoinerBot

####Create environment:

	virtualenv .env

####Activate it:

	source .env/bin/activate

####Install requirements:

	pip install -r requirements.pip

####Now we need to configure settings:

	[@BotFather](https://telegram.me/botfather) will give you TG_API_TOKEN.
	BITCOIN_RPC you can get from your bitcoind.
	ADMIN_IDS - id admin telegram ids list.
	Also dont forget place rates.py and reciver.py to crontab!
	Run it with *python bot.py*.





