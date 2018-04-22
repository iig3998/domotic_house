#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import telepot
import time
import json
import sys
import select
from socket import *
from emoji import emojize
import threading
from threading import Timer
from threading import Thread
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s')
logger_alarm = logging.getLogger(__name__)

threads = []
sockets = []
status_alarm = 0
sem_send_message = threading.Lock()
sem_status_alarm = threading.Lock()

BUFFER_SIZE = 4 # 4 byte

# Multithreaded Sensor server
class ClientThread(Thread):

	# Init thread client object
	def __init__(self, ip, conn, chat_id, bot, delta):

		logger_alarm.info("Init thread client")

		Thread.__init__(self)
		self._ip_client_alarm = ip
		self._conn = conn
		self._running_client_alarm = True
		self._chat_id = chat_id
		self._bot = bot
		self._checksum = 0xAA
		self._delta = delta
		logger_alarm.info("New client sensor thread init for " + str(self._ip_client_alarm))

		return

	# Delete thread client object
	def __del__(self):

		logger_alarm.info("Delete thread client object")

		return

	# Run thread
	def run(self):

		global status_alarm
		logger_alarm.info("Start thread client")

		while self._running_client_alarm:

			# Get status alarm
			sem_status_alarm.acquire()
			tmp_status_alarm = status_alarm
			sem_status_alarm.release()

			if tmp_status_alarm == 0:
				try:
					dummy = self._conn.recv(BUFFER_SIZE)
				except KeyboardInterrupt:
					break
			elif tmp_status_alarm == 1:
				try:
					data = self._conn.recv(BUFFER_SIZE)
				except KeyboardInterrupt:
					logger_alarm.error("Close socket %s" + str(self._ip_client_alarm))
					break

				if not data:
					logger_alarm.info("Lost connection with " + str(self._ip_client_alarm))
					break
				elif (len(data) != BUFFER_SIZE):
					logger_alarm.info("Len data received from %s client is wrong", str(self._ip_client_alarm))
				elif status_alarm == 1:
					last = int(time.time())
					logger_alarm.info("Receive data from client: " + str(self._ip_client_alarm))
					chk = (data[0] + data[1] + data[2] + self._checksum) & 0xFF
					now = int(time.time())
					if (chk == data[3]) and ((now - last) > self._delta) and data[0] == 0xFD:
						last = now
						self.send_message_alarm(data[1])

		logger_alarm.info("Terminate thread client")
		self._conn.close()

		return 0

	# send message alarm
	def send_message_alarm(self, value):

		logger_alarm.info("Send alarm")

		# Acquire semaphore
		sem_send_message.acquire()

		try:
			self._bot.sendMessage(self._chat_id, "Allarme rilevato da sensore %s" % value)
		except TelegramError as e:
			logger_alarm.info("Error send message to bot " + str(e))
			sem_send_message.release()
			return -1

		# Release semaphore
		sem_send_message.release()

		return 0

# Class alarm object
class Alarm():

	# Init alarm object
	def __init__(self, name, chat_id, bot):

		logger_alarm.info("Init alarm object")

		self._name = name
		self._status_thread_alarm = True
		self._check_alarm = False
		self._chat_id = chat_id
		self._bot = bot
		self._delta = 0

		# Configuration server
		self._ip_server = None
		self._port_server = None
		self._serversocket = None

		# Configuration client
		self._client_socket = None
		self._client_ip = None

		return

	# Delete alarm object
	def __del__(self):

		logger_alarm.info("Delete alarm object")

		self._serversocket.close()

		return


	# Read configuration file server alarm
	def read_configuration_file(self):

		logger_alarm.info("Read configuration file server alarm")

		try:
			with open('conf.json', 'r') as data_file:
				data = json.load(data_file)
		except:
			logger_alarm.error("File conf.json not found")
			return -1

		self._ip_server = data["server_alarm"][0]["ip_server"]
		self._port_server = data["server_alarm"][0]["port"]
		self._delta = data["server_alarm"][0]["delta"]

		return 0


	# Init server alarm
	def init_server_alarm(self):

		logger_alarm.info("Init server alarm")

		# Start server
		self._serversocket = socket(AF_INET, SOCK_STREAM)
		self._serversocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

		try:
			self._serversocket.bind((self._ip_server, self._port_server))  
		except socket.error as e:
			logger_alarm.error("Bind failed. Error: " + str(e))
			sys.exit(-1)

		logger_alarm.info("Waiting connection from alarm client ....")
		self._serversocket.listen(10)
		self._thread_alarm = threading.Thread(target = self.conn_sensor_thread)
		self._thread_alarm.daemon = True
		self._thread_alarm.start()

		return 0

	# Server listen connection
	def conn_sensor_thread(self):

		while True: 
			logger_alarm.info("System server alarm: Waiting for connections from sensors ...")
			(client_socket, client_ip) = self._serversocket.accept()
			logger_alarm.info("Accepting connection from " + str(client_ip))

			try:
				newthread_sensor_alarm = ClientThread(client_ip, client_socket, self._chat_id, self._bot, self._delta)
			except:
				logger_alarm.error("Error create thread client " + str(e))
				continue

			newthread_sensor_alarm.start()
			threads.append(newthread_sensor_alarm)
			sockets.append(client_socket)

		return 0

	# Terminate thread alarm
	def terminate_alarm(self):

		logger_alarm.info("Terminate sensor thread")

		self._serversocket.close()

		# Close all socket client
		for sck in sockets:
			sck.close()

		# Terminate all threads client
		for thr in threads:
			thr._running_client_alarm = False
			thr.join()

		return 0

	# Active alarm afetr n seconds
	def _active_alarm(self):

		global status_alarm
		self._bot.sendMessage(self._chat_id, "Allarme attivato")

		sem_status_alarm.acquire()
		status_alarm = 1
		sem_status_alarm.release()

		return 0

	# Active alarm
	def activate_alarm(self):

		global status_alarm
		logger_alarm.info("Active alarm")

		t = Timer(10.0, self._active_alarm)
		t.start()

		return 0

	# Deactive alarm
	def deactive_alarm(self):

		global status_alarm
		logger_alarm.info("Deactive alarm")

		sem_status_alarm.acquire()
		status_alarm = 0
		sem_status_alarm.release()

		return 0

	# Get status alarm
	def get_status_alarm(self):

		global status_alarm
		logger_alarm.info("Get status alarm")

		sem_status_alarm.acquire()
		tmp_status_alarm = status_alarm
		sem_status_alarm.release()

		if tmp_status_alarm == 1:
			logger_alarm.info("Alarm active")
			return 1
		elif tmp_status_alarm == 0:
			logger_alarm.info("Alarm deactive")
			return 0

		return -1

	# Manage alarm
	def manage_alarm(self):

		logger_alarm.info("Send alarm keyboard")

		markup = InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text = "Attiva allarme", callback_data = "active_alarm")],
			[InlineKeyboardButton(text = "Disattiva allarme", callback_data = "deactive_alarm")],
			[InlineKeyboardButton(text = "Stato allarme", callback_data = "status_alarm")],
			[InlineKeyboardButton(text = "Menù comandi", callback_data = "main_command")],
			])

		try:
			self._bot.sendMessage(self._chat_id, "** COMANDI ALLARME **", reply_markup = markup)
		except TelegramError as e:
			logger_alarm.error("Error send message to bot " + str(e))

		return 0

	# Main command
	def get_main_menu(self):

		logger_alarm.info("Get main command from alarm menù")

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
			logger_alarm.error("Error send message to bot " + str(e))

		return 0

	# Query alarm
	def callback_query_alarm(self, query_id, data):

		logger_alarm.info("Callback query alarm")

		if data == "alarm":
			self._bot.answerCallbackQuery(query_id, text = "")
			self.manage_alarm()
			return 1
		if data == "active_alarm":
			self.activate_alarm()
			self._bot.answerCallbackQuery(query_id, text = "Allarme attivo tra 10 secondi")
			return 1
		elif data == "deactive_alarm":
			self.deactive_alarm()
			self._bot.answerCallbackQuery(query_id, text = "Allarme disattivato")
			return 1
		elif data == "status_alarm":
			ret = self.get_status_alarm()
			if ret == 1:
				self._bot.answerCallbackQuery(query_id, text = "Allarme attivo")
			elif ret == 0:
				self._bot.answerCallbackQuery(query_id, text = "Allarme non attivo")
			return 1
		elif data == "main_command":
			self._bot.answerCallbackQuery(query_id, text = "")
			self.get_main_menu()
			return 1

		return 0
