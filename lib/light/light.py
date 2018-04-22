#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import telepot
import json
from emoji import emojize
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from .modbus.cmd_light import Modbus

logging.basicConfig(level = logging.INFO, format = '%(asctime)s %(levelname)-8s %(message)s')
logger_light = logging.getLogger(__name__)

# Class light
class Light():

	# Init light object
	def __init__(self, name, chat_id, bot):

		logger_light.info("Init light object")

		self._name = name
		self._master = Modbus()
		self._chat_id = chat_id
		self._bot = bot

		# Address modbus room
		self._kitchen_address = None
		self._living_room_address = None
		self._bathroom_address = None
		self._bedroom_1_address = None
		self._bedroom_2_address = None

		return

	# Delete light object
	def __del__(self):

		logger_light.info("Delete light object")

		del self._master

		return

	# Manage light
	def manage_light(self):

		logger_light.info("Send light keyboard")

		markup = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text = "Cucina", callback_data = "kitchen_room")],
			[InlineKeyboardButton(text = "Soggiorno", callback_data = "living_room")],
			[InlineKeyboardButton(text = "Bagno", callback_data = "bathroom")],
			[InlineKeyboardButton(text = "Camera da letto", callback_data = "bedroom")],
			[InlineKeyboardButton(text = "Menù comandi", callback_data = "main_command")],
			])

		try:
			self._bot.sendMessage(self._chat_id, "** SELEZIONA STANZA **", reply_markup = markup)
		except TelegramError as e:
			logger_light.error("Error send message to bot " + str(e))

		return 0

	# Read modbus address configuration
	def read_configuration_file(self):

		logger_light.info("Read configuration for relay modbus")

		try:
			with open('conf.json', 'r') as data_file:
				data = json.load(data_file)
		except:
			logger_main.error("File conf.json not found")
			return -1

		# Read address modbus configuration
		self._kitchen_address = data["address_modbus"][0]["kitchen_address"]
		self._living_room_address = data["address_modbus"][0]["living_room_address"]
		self._bathroom_address = data["address_modbus"][0]["bathroom_address"]
		self._bedroom_1_address = data["address_modbus"][0]["bedroom_1_address"]
		self._bedroom_2_address = data["address_modbus"][0]["bedroom_2_address"]

		return 0
   
	# Main command
	def get_main_menu(self):

		logger_light.info("Get main command from light menù")

		markup = InlineKeyboardMarkup(inline_keyboard = [
			[InlineKeyboardButton(text = "Luci " + emojize(":bulb:", use_aliases = True), callback_data = "light")],
			[InlineKeyboardButton(text = "Radio " + emojize(":radio:", use_aliases = True), callback_data = "radio")],
			[InlineKeyboardButton(text = "Volume " + emojize(":sound:", use_aliases = True), callback_data = "volume")],
			[InlineKeyboardButton(text = "Videocamera " + emojize(":video_camera:", use_aliases = True), callback_data = "videocamera")],
			[InlineKeyboardButton(text = "Allarme " + emojize(":rotating_light:", use_aliases = True), callback_data = "alarm")],
			])

		try:
			self._bot.sendMessage(self._chat_id, "** COMANDI **", reply_markup = markup)
		except TelegramError as e:
			logger_light.error("Error send message to bot " + str(e))
			return -1

		return 0

	# Kitchen room
	def kitchen_room(self):

		logger_light.info("Send kitchen keyboard")

		markup = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text = "Interruttore cucina", callback_data = "switch_kitchen_room")],
			[InlineKeyboardButton(text = "Menù stanze", callback_data = "light")]
			])

		try:
			self._bot.sendMessage(self._chat_id, "** INTERRUTTORE CUCINA **", reply_markup = markup)
		except TelegramError as e:
			logger_light.error("Error send message to bot " + str(e))
			return -1

		return 0

	# Living room
	def living_room(self):

		logger_light.info("Send living room keyboard")

		markup = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text = "Interruttore soggiorno", callback_data = "switch_living_room")],
			[InlineKeyboardButton(text = "Menù stanze", callback_data = "light")]
			])

		try:
			self._bot.sendMessage(self._chat_id, "** INTERRUTTORE SOGGIORNO **", reply_markup = markup)
		except TelegramError as e:
			logger_light.error("Error send message to bot " + str(e))
			return -1

		return 0

	# Bathroom
	def bathroom(self):

		logger_light.info("Send bathroom keyboard")

		markup = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text = "Interruttore bagno", callback_data = "switch_bathroom")],
			[InlineKeyboardButton(text = "Menù stanze", callback_data = "light")],
			])

		try:
			self._bot.sendMessage(self._chat_id, "** INTERRUTTORE BAGNO **", reply_markup = markup)
		except TelegramError as e:
			logger_light.error("Error send message to bot " + str(e))
			return -1

		return 0

	# Bedroom
	def bedroom(self):

		logger_light.info("Send bedroom keyboard")

		markup = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text = "Interruttore camera da letto", callback_data = "switch_bedroom")],
			[InlineKeyboardButton(text = "Menù stanze", callback_data = "light")],
			])

		try:
			self._bot.sendMessage(self._chat_id, "** INTERRUTTORE STANZA DA LETTO **", reply_markup = markup)
		except TelegramError as e:
			logger_light.error("Error send message to bot " + str(e))
			return -1

		return 0

	# Switch light kitchen
	def switch_kitchen_room(self):

		logger_light.info("switch_kitchen_room")

		channel = self._kitchen_address
		self._master.toggle_relay(channel, 1)
		ret = self._master.read_status_relay(channel, 1)

		return ret

	# Switch light living room
	def switch_living_room(self):

		logger_light.info("switch_living_room")

		channel = self._living_room_address
		self._master.toggle_relay(channel, 1)
		ret = self._master.read_status_relay(channel, 1)

		return ret

	# Switch light bathroom
	def switch_bathroom(self, chat_id, bot):

		logger_light.info("switch_bathroom")

		channel = self._bathroom_address
		ret = self._master.read_status_relay(channel, 2)

		return ret

	# Switch light bedroom
	def switch_bedroom(self, chat_id, bot):

		logger_light.info("switch_bedroom")

		channel = self._bedroom_1_address
		ret = self._master.read_status_relay(channel, 2)

		return ret

	# Query light
	def callback_query_light(self, query_id, data):

		logger_light.info("Callback query light")

		if data == "light":
			self._bot.answerCallbackQuery(query_id, text = "")
			self.manage_light()
			return 1
		elif data == "kitchen_room":
			self._bot.answerCallbackQuery(query_id, text = "")
			self.kitchen_room()
			return 1
		elif data == "living_room":
			self._bot.answerCallbackQuery(query_id, text = "")
			self.living_room()
			return 1
		elif data == "bathroom":
			self._bot.answerCallbackQuery(query_id, text = "")
			self.bathroom()
			return 1
		elif data == "bedroom":
			self._bot.answerCallbackQuery(query_id, text = "")
			self.bedroom()
			return 1
		elif data == "switch_kitchen_room":
			ret = self.switch_kitchen_room()
			if ret == 0:
				self._bot.answerCallbackQuery(query_id, text = "Luci cucina spente")
			elif ret == 1:
			 	self._bot.answerCallbackQuery(query_id, text = "Luci cucina accese")
			return 1
		elif data == "switch_living_room":
			ret = self.switch_living_room()
			if ret == 0:
				self._bot.answerCallbackQuery(query_id, text = "Luci soggiorno spente")
			elif ret == 1:
			 	self._bot.answerCallbackQuery(query_id, text = "Luci soggiorno accese")
			return 1
		elif data == "switch_bathroom":
			ret = self.switch_bathroom()
			if ret == 0:
				self._bot.answerCallbackQuery(query_id, text = "Luci bagno spente")
			elif ret == 1:
			 	self._bot.answerCallbackQuery(query_id, text = "Luci bagno accese")
			return 1
		elif data == "switch_bedroom":
			ret = self.switch_bedroom()
			if ret == 0:
				self._bot.answerCallbackQuery(query_id, text = "Luci bagno spente")
			elif ret == 1:
			 	self._bot.answerCallbackQuery(query_id, text = "Luci bagno accese")
			return 1
		elif data == "main_command":
			self._bot.answerCallbackQuery(query_id, text = "")
			self.get_main_menu()
			return 1

		return 0