#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import subprocess
from emoji import emojize
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')
logger_volume = logging.getLogger(__name__)

# Class volume
class Volume():

	# Init Volume object
	def __init__(self, name, chat_id, bot):

		logger_volume.info("Init volume object")

		self._name = name
		self._chat_id = chat_id
		self._bot = bot

		return

	def __del__(self):

		logger_volume.info("Delete volume object")

		return

	# Manage volume
	def manage_volume(self):

		logger_volume.info("Send volume command")

		markup = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text = "Aumenta volume", callback_data = "increment_volume")],
			[InlineKeyboardButton(text = "Abbassa volume", callback_data = "decrement_volume")],
			[InlineKeyboardButton(text = "Mute", callback_data = "mute_volume")],
			[InlineKeyboardButton(text = "On Mute", callback_data = "on_mute_volume")],
			[InlineKeyboardButton(text = "Menù principale", callback_data = "main_command")],
			])

		try:
			self._bot.sendMessage(self._chat_id, "** COMANDI VOLUME **", reply_markup = markup)
		except TelegramError as e:
			logger_volume.error("Error send message to bot " + str(e))
			return -1

		return 0

	# Main command
	def get_main_menu(self, chat_id, bot):

		logger_volume.info("Get main command from volume menù")

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
			logger_volume.error("Error send message to bot " + str(e))
			return -1

		return 0

	# Store value volume
	def store_volume(self):

		logger_volume.info("Store volume")

		try :
		        subprocess.call(["alsactl", "store"])
		except subprocess.CalledProcessError as error:
			logger_volume.error(error.output)
			return -1

		return 0

	# Increment volume
	def increment_volume(self):

		logger_volume.info("Increment volume")

		try :
			# amixer -q sset 'Lineout volume control' 3%+
			subprocess.call(["amixer", "-q", "sset", "'Lineout volume control'", "3%+"])
		except subprocess.CalledProcessError as error:
			logger_volume.error(error.output)
			return -1

		return 0

	# Decrement volume
	def decrement_volume(self):

		logger_volume.info("Decrement volume")

		try:
			# amixer -q sset 'Lineout volume control' 3%-
			subprocess.call(["amixer", "-q", "sset", "'Lineout volume control'", "3%-"])
		except subprocess.CalledProcessError as error:
			logger_volume.error(error.output)
			return -1

		return 0

	# Mute volume
	def mute_volume(self):

		logger_volume.info("Mute volume")

		try:
			subprocess.call(["amixer", "cset", "numid=6", "off"])
		except subprocess.CalledProcessError as error:
			logger_volume.error(error.output)
			return -1

		return 0

	# Unmute volume
	def on_mute_volume(self):

		logger_volume.info("On mute volume")

		try:
			subprocess.call(["amixer", "cset", "numid=10", "on"])
		except subprocess.CalledProcessError as error:
			logger_volume.error(error.output)
			return -1

		return 0

	# Callback function query volume
	def callback_query_volume(self, query_id, data):

		logger_volume.info("Callback query volume")

		if data == "volume":
			self._bot.answerCallbackQuery(query_id, text = "")
			self.manage_volume()
			return 1
		elif data == "increment_volume":
			self._bot.answerCallbackQuery(query_id, text = "Increased volume")
			self.increment_volume()
			return 1
		elif data == "decrement_volume":
			self._bot.answerCallbackQuery(query_id, text = "Decremented volume")
			self.decrement_volume()
			return 1
		elif data == "mute_volume":
			self._bot.answerCallbackQuery(query_id, text = "Mute volume")
			self.mute_volume()
			return 1
		elif data == "on_mute_volume":
			self._bot.answerCallbackQuery(query_id, text = "OnMute volume")
			self.on_mute_volume()
			return 1
		elif data == "main_command":
			self._bot.answerCallbackQuery(query_id, text = "")
			self.get_main_menu()
			return 1

		return 0