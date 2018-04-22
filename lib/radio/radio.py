#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import subprocess
import json
from emoji import emojize
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')
logger_radio = logging.getLogger(__name__)

# Class radio
class Radio():

	# Init radio object
	def __init__(self, name, chat_id, bot):

		logger_radio.info("Init radio object")

		self._name = name
		self._flag_select_station = 0
		self._chat_id = chat_id
		self._bot = bot
		self._radio_list = {}

		return

	# Delete radio object
	def __del__(self):

		logger_radio.info("Delete radio object")

		self._flag_select_station = 0

		return

	# Read configuration bot
	def read_configuration_file(self):

		logger_radio.info("Read list radio station")

		try:
			with open('conf.json', 'r') as data_file:
				data = json.load(data_file)
		except:
			logger_radio.error("File conf.json not found")
			return -1

		idx = 0
		for key, value in data["radio_list"].items():

			self._radio_list.update({idx: (str(key), str(value))})
			idx += 1

		return 0

	# Main command
	def get_main_menu(self):

		logger_radio.info("Get main command from light menù")

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
			logger_radio.error("Error send message to bot " + str(e))
			return -1

		return 0

	# Manage radio
	def manage_radio(self):

		logger_radio.info("Send radio keyboard")

		markup = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text = "Seleziona stazione", callback_data = "select_station")],
			[InlineKeyboardButton(text = "Spegni radio", callback_data = "power_off_radio")],
			[InlineKeyboardButton(text = "Menù comandi", callback_data = "main_command")]
			])

		try:
			self._bot.sendMessage(self._chat_id, "** COMANDI RADIO **", reply_markup = markup)
		except TelegramError as e:
			logger_radio.error("Error send message to bot " + str(e))
			return -1

		return 0

	# Select station radio keyboard
	def select_station(self):

		markup = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text = self._radio_list[0][0],  callback_data = self._radio_list[0][0]),
			InlineKeyboardButton(text  = self._radio_list[1][0],  callback_data = self._radio_list[1][0])],
			[InlineKeyboardButton(text = self._radio_list[2][0],  callback_data = self._radio_list[2][0]),
			InlineKeyboardButton(text  = self._radio_list[3][0],  callback_data = self._radio_list[3][0])],
			[InlineKeyboardButton(text = self._radio_list[4][0],  callback_data = self._radio_list[4][0]),
			InlineKeyboardButton(text  = self._radio_list[5][0],  callback_data = self._radio_list[5][0])],
			[InlineKeyboardButton(text = self._radio_list[6][0],  callback_data = self._radio_list[6][0]),
			InlineKeyboardButton(text  = self._radio_list[7][0],  callback_data = self._radio_list[7][0])],
			[InlineKeyboardButton(text = self._radio_list[8][0],  callback_data = self._radio_list[8][0]),
			InlineKeyboardButton(text  = self._radio_list[9][0],  callback_data = self._radio_list[9][0])],
			[InlineKeyboardButton(text = self._radio_list[10][0], callback_data = self._radio_list[10][0]),
			InlineKeyboardButton(text  = self._radio_list[11][0], callback_data = self._radio_list[11][0])],
			[InlineKeyboardButton(text = self._radio_list[12][0], callback_data = self._radio_list[12][0]),
			InlineKeyboardButton(text  = self._radio_list[13][0], callback_data = self._radio_list[13][0])],
			[InlineKeyboardButton(text = self._radio_list[14][0], callback_data = self._radio_list[14][0]),
			InlineKeyboardButton(text  = self._radio_list[15][0], callback_data = self._radio_list[15][0])],
			[InlineKeyboardButton(text = self._radio_list[16][0], callback_data = self._radio_list[16][0]),
			InlineKeyboardButton(text  = self._radio_list[17][0], callback_data = self._radio_list[17][0])],
			[InlineKeyboardButton(text = self._radio_list[18][0], callback_data = self._radio_list[18][0]),
			InlineKeyboardButton(text  = self._radio_list[19][0], callback_data = self._radio_list[19][0])],
			[InlineKeyboardButton(text = self._radio_list[20][0], callback_data = self._radio_list[20][0]),
			InlineKeyboardButton(text  = self._radio_list[21][0], callback_data = self._radio_list[21][0])],
			[InlineKeyboardButton(text = self._radio_list[22][0], callback_data = self._radio_list[22][0]),
			InlineKeyboardButton(text  = self._radio_list[23][0], callback_data = self._radio_list[23][0])],
			[InlineKeyboardButton(text = self._radio_list[24][0], callback_data = self._radio_list[24][0]),
			InlineKeyboardButton(text  = self._radio_list[25][0], callback_data = self._radio_list[25][0])],
			[InlineKeyboardButton(text = "Comandi radio", callback_data = "manage_radio")]
			])

		try:
			message_with_inline_keyboard = self._bot.sendMessage(self._chat_id, "** STAZIONI RADIO **", reply_markup = markup)
		except:
			logger_radio.error("Error send message to bot")

		return 0

	# Power off radio
	def power_off_radio(self):

		logger_radio.info("Kill mplayer radio streaming")

		try:
			subprocess.call("pkill mplayer", shell = True)
			return 0
		except subprocess.CalledProcessError as error:
			logger_radio.info(error.output)
			return -1

	# Command radio query
	def callback_query_radio(self, query_id, data):

		logger_radio.info("Callback query radio")

		if data == "radio":
			self._bot.answerCallbackQuery(query_id, text = "")
			self.manage_radio()
			return 1
		elif data == "select_station":
			self._flag_select_station = 1
			self._bot.answerCallbackQuery(query_id, text = "")
			self.select_station()
			return 1
		elif data == "power_off_radio":
			self._bot.answerCallbackQuery(query_id, text = "")
			self.power_off_radio()
			return 1
		elif data == "manage_radio":
			self._flag_select_station = 0
			self._bot.answerCallbackQuery(query_id, text = "")
			self.manage_radio()
			return 1
		elif data == "main_command":
			self._bot.answerCallbackQuery(query_id, text = "")
			self.get_main_menu()
			return 1
		elif self._flag_select_station == 1:
			self.power_off_radio()
			self._bot.answerCallbackQuery(query_id, text = "")

			for i in range(0, len(self._radio_list)):
				if data == self._radio_list[i][0]:
					try:
						logger_radio.info("play radio %s" % self._radio_list[i][1])
						subprocess.call("radio %s" % self._radio_list[i][1], shell = True)
						return 1
					except subprocess.CalledProcessError as error:
						logger_radio.error(error.output)
						return -1

			logger_radio.error("Radio station not found")
			return -1

		return 0