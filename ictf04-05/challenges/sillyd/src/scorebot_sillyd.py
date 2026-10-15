#!/usr/bin/python

#
# scorebot script for sillyd
#
#
# Syntax: scorebot_sillyd.py <host> <new flag> [<old cookie>]
#

import os, random, time, sys, string, socket

target  = sys.argv[1]
newflag = sys.argv[2]

if len(sys.argv) > 3 and sys.argv[3] != "":
	cookie = sys.argv[3]
else:
	cookie = ""

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

if s.connect_ex((target, 12345)) == 0:
	# read the welcome banner
	banner = s.recv(1024)

	# test PING command
	np = 1 + random.randint(1,42)
	ping = "PING " + str(np) + "\r\n"
	#print ping
	s.send(ping)
	for i in range(0,np):
		pong = ""
		pong = s.recv(7)
		#print pong

	# get FLAG 
	if cookie != "":
		s.send("AUTH " + cookie + "\r\n")
		tmp = s.recv(1024)
		#print "tmp=" + tmp
		if tmp[0] == "+":
			flag = s.recv(1024)
			print "FLAG:" + flag

	# set FLAG
	s.send("REG " + newflag + "\r\n")
	tmp = s.recv(1024)
		#print "tmp=" + tmp
	if tmp[0] == "+":
		new_cookie = s.recv(1024)
		print "COOKIE:" + new_cookie

	# disconnect
	s.send("QUIT")
	tmp = s.recv(7)

	s.close()

else:
	sys.exit(1)
