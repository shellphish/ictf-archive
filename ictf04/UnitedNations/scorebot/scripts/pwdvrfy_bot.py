#! /usr/bin/python

import socket

import os, random, time, sys, string, re


alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
            'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 
            's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def getRandomString(len):
	ret = ""
	for i in range(len):
		ret += random.choice(alphabet)
	return ret


#### Main
target   = sys.argv[1]
port     = 11111
newflag  = sys.argv[2]
if len(sys.argv) > 3:
	cookie = sys.argv[3]
	username = cookie
else:
	cookie = ""
	username = ""

oldflag = ""

if username != "":
   try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((target, port))
	s.send('DICT %s\n'%username)
	file = s.makefile()
	oldflag = file.readline()
	oldflag = oldflag[:-1]
	s.close()
   except Exception, e:
      print "Exception getting flag %s" % (e)

newuser   = getRandomString(8)
newcookie = newuser

try:
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.connect((target, port))
   s.send('STORE %s %s\n'%(newuser,newflag))
   s.close()
except Exception, e:
   print "Exception setting flag %s" % (e)

print "FLAG:" + oldflag
print "COOKIE:" + newcookie
 
