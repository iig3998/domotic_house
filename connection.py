#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import signal
import time
import logging
import subprocess
import http.client as httplib

main_string = " 'python3 main.py' "
server_string = " 'python3 server.py' "

logging.basicConfig(level = logging.INFO, format = '%(asctime)s %(levelname)-8s %(message)s')
logger_connection = logging.getLogger(__name__)

# Kill process
def signal_handler(signal, frame):

	  logger_connection.info("You pressed Ctrl-C")

	  # KIll main process
	  kill_process(main_string)
	  # KIll server process
	  kill_process(server_string)

	  sys.exit(0)

# Kill process
def kill_process(name_process):

	process = subprocess.Popen("ps aux | grep " + name_process + " | grep -v grep | awk '{ print $2 }'", shell = True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	out, err = process.communicate()
	if len(out.decode('ascii')) == 0:
		logger_connection.info("No process %s running" % name_process)
		return -1

	logger_connection.info("Kill process %s", str(out.decode('ascii')))
	cmd = "kill -9 " + str(out.decode('ascii'))
	subprocess.call(cmd, shell=True)

	return 0

# Check status connection
def have_internet():

	conn = httplib.HTTPConnection("www.google.com", timeout = 5)

	try:
		conn.request("HEAD", "/")
		conn.close()
		return True
	except:
		conn.close()
		return False

# Main program
if __name__ == "__main__":

	pid_process = 0
	state = False
	
	signal.signal(signal.SIGINT, signal_handler)

	while True:
		
		if state == True:
			if old_state != state:
				logger_connection.info("Start main.py")
				subprocess.call(" python3 main.py &", shell = True)
				time.sleep(1)
		elif state == False:
			logger_connection.info("Lost connection!")
			kill_process(main_string)
			kill_process(server_string)

		old_state = state
		state = have_internet()
		time.sleep(5)

	sys.exit(0)
