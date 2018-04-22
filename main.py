#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import json
import signal
from emoji import emojize
from lib.light.light import *
from lib.radio.radio import *
from lib.volume.volume import *
from lib.alarm.alarm import *
from telepot.loop import MessageLoop

# Global variable
global light
global radio
global volume
global alarm

# Logging object
logging.basicConfig(level = logging.INFO, format = '%(asctime)s %(levelname)-8s %(message)s')
logger_main = logging.getLogger(__name__)

class ConnectionBot():

	# Init bot telegram
	def __init__(self):

		logger_main.info("Init telegram bot")

		self._first_name = None
		self._last_name = None
		self._token = None
		self._chat_id = None
		self._bot = None

		return

	# Read configuration bot
	def read_configuration_file(self):

		logger_main.info("Read configuration for bot")

		try:
			with open('conf.json', 'r') as data_file:
				data = json.load(data_file)
		except:
			logger_main.error("File conf.json not found")
			return -1

		self._token = data["conf"][0]["token"]
		self._first_name = data["conf"][0]["first_name"]
		self._last_name = data["conf"][0]["last_name"]
		self._chat_id = data["conf"][0]["chat_id"]

		return 0

	# Get info bot created
	def get_info_bot(self):

		logger_main.info("First Name: %s" % self._first_name)
		logger_main.info("Last Name: %s" % self._last_name)
		logger_main.info("Chat id: %s" % self._chat_id)

		return 0

# Message on chat
def on_chat_message(msg):

	content_type, chat_type, chat_id = telepot.glance(msg)

	# Check chat_id
	if chat_id != int(Casa._chat_id):
		logger_main.info("Chat id is not valid!")

		try:
			Casa._bot.sendMessage(Casa._chat_id, "User not autorizzated %s" % chat_id, reply_markup = None)
			Casa._bot.sendMessage(Casa._chat_id, "401 - Unauthorized", reply_markup = None)
		except TelegramError as e:
			logger_main.error("Error send message to bot " + str(e))

		return -1

	if content_type != 'text':
		logger_main.error("Invalid message type")

		return -1

	command = msg['text'][0:6].lower()
	markup = InlineKeyboardMarkup(inline_keyboard = [
		[InlineKeyboardButton(text = "Luci " + emojize(":bulb:", use_aliases = True), callback_data = "light")],
		[InlineKeyboardButton(text = "Radio " + emojize(":radio:", use_aliases = True), callback_data = "radio")],
		[InlineKeyboardButton(text = "Volume " + emojize(":sound:", use_aliases = True), callback_data = "volume")],
		[InlineKeyboardButton(text = "Videocamera " + emojize(":video_camera:", use_aliases = True), callback_data = "videocamera")],
		[InlineKeyboardButton(text = "Allarme " + emojize(":rotating_light:", use_aliases = True), callback_data = "alarm")],
		])

	# Send main keyboard
	if command == '/start':
		try:
			Casa._bot.sendMessage(chat_id, "** COMANDI **", reply_markup = markup)
		except TelegramError as e:
			logger_main.error("Error send message to bot " + str(e))
	else:
		try:
			Casa._bot.sendMessage(Casa._chat_id, "Comando non valido", reply_markup=markup)
		except TelegramError as e:
			logger_main.error("Error send message to bot " + str(e))

	return 0

# Callback query
def on_callback_query(msg):

	logger_main.info("on_callback_query")

	if msg == None:
		logger_main.error("Error, message is empty!")
		return -1

	query_id, from_id, data = telepot.glance(msg, flavor = "callback_query")

	ret = light.callback_query_light(query_id, data)
	if ret == 1:
		logger_main.info("Callback query light")
		return 1

	ret = radio.callback_query_radio(query_id, data)
	if ret == 1:
		logger_main.info("Callback query radio")
		return 1

	ret = volume.callback_query_volume(query_id, data)
	if ret == 1:
		logger_main.info("Callback query volume")
		return 1

	ret = alarm.callback_query_alarm(query_id, data)
	if ret == 1:
		logger_main.info("Callback query alarm")
		return 1

	logger_main.error("Error, no command found")

	return 0

# Signal_handler function
def signal_handler(signal, frame):

	global light
	global radio
	global volume
	global alarm

	logger_main.info("You pressed Ctrl-C")

	# Destroy object
	logger_main.info("Destroy object!")

	alarm.terminate_alarm()
	del light
	del radio 
	del volume
	del alarm
        
	sys.exit(0)

# Main programm
if __name__ == "__main__":

	light = None
	radio = None
	volume = None
	alarm = None

	# Sighandler
	signal.signal(signal.SIGINT, signal_handler)

	# Init authentication
	Casa = ConnectionBot()

	# Reda configuration file bot
	ret = Casa.read_configuration_file()
	if ret == -1:
	    logger_main.error("Error init authentication")
	    sys.exit(-1)

	# Create bot
	Casa._bot = telepot.Bot(Casa._token)

	# Get info bot
	Casa.get_info_bot()

	# Create light object
	light = Light("Light", Casa._chat_id, Casa._bot)
	ret = light.read_configuration_file()
	if ret == -1:
		logger_main.error("Error load light configuration")
		sys.exit(-1)

	# Create radio object
	radio = Radio("Radio", Casa._chat_id, Casa._bot)
	ret = radio.read_configuration_file()
	if ret == -1:
		logger_main.error("Error load radio configuration")
		sys.exit(-1)

	# Create volume object
	volume = Volume("Volume", Casa._chat_id, Casa._bot)

	# Create alarm object
	alarm = Alarm("Alarm", Casa._chat_id, Casa._bot)
	ret = alarm.read_configuration_file()
	if ret == -1:
		logger_main.error("Error load alarm configuration")
		sys.exit(-1)

	alarm.init_server_alarm()

	# Run thread telepot
	MessageLoop(Casa._bot, {
				"chat": on_chat_message,
				"callback_query": on_callback_query,
				}).run_as_thread()

	logger_main.info("Listening ...")

	# Loop
	while True:
		time.sleep(10)

	# Destroy object
	logging.info("Destroy object")

	MessageLoop.cancel()

	alarm.terminate_alarm()
	del light
	del radio
	del volume
	del alarm

	sys.exit(0)