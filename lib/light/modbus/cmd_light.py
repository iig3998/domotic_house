#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
from pymodbus3.client.sync import ModbusSerialClient as ModbusClient

logging.basicConfig(level = logging.INFO, format = '%(asctime)s %(levelname)-8s %(message)s')
logger_modbus = logging.getLogger(__name__)

PORT = '/dev/ttyUSB0'
BAUDRATE = '9600'
PARITY = 'N'
BITS = 8

class bcolors:

	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

# Class Modbus
class Modbus():

	# Init modbus device
	def __init__(self):

		self._client = ModbusClient(method='rtu',
			port = PORT,
			bytesize = BITS,
			parity = PARITY,
			baudrate = BAUDRATE,
			timeout = 1)

		if self._client.connect() == False:
			logger_modbus.error(bcolors.FAIL + "*******************************" + bcolors.ENDC)
			logger_modbus.error(bcolors.FAIL + "*** ERROR, DEVICE NOT FOUND ***" + bcolors.ENDC)
			logger_modbus.error(bcolors.FAIL + "*******************************" + bcolors.ENDC)
			time.sleep(1)

		return

	# Delete modbus device
	def __del__(self):

		logger_modbus.info("Delete modbus device")

		self.close_connection()

		return

	# Toggle relay
	def toggle_relay(self, channel, address):

		try:
			ret = self._client.write_register(channel, 0x0300, unit=address)
		except:
			logger_modbus.error(bcolors.FAIL + "Error, slave %s not responde!"  + bcolors.ENDC, address)
			return -1

		logger_modbus.info("Toggle relay %s" %ret)

		return ret

	# Read status relay
	def read_status_relay(self, channel, address):

		try:
			ret = self._client.read_holding_registers(channel, unit=address)
		except:
			logger_modbus.error(bcolors.FAIL + "Error, slave %s not responde!" + bcolors.ENDC, address)
			return -1

		logger_modbus.info("Status relay channel %d: %s" % (channel, int(ret.registers[0])))

		return int(ret.registers[0])

	# Close device
	def close_connection(self):

	    logger_modbus.info("Close connection!")

	    self._client.close()

	    return 0