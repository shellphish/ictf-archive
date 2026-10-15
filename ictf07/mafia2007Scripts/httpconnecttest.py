#! /usr/bin/python

"""


"""

#system imports
import os
import random
import time
import sys
import string
import re
import socket

myDebug = 0


alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
            'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 
            's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def getRandomString(len):
  ret = ""
  for i in range(len):
    ret += random.choice(alphabet)
  return ret


### MAIN ###

if len( sys.argv ) < 2:
  print "usage: %s <host>" % sys.argv[0]
  sys.exit( 1 )
  

try:
  s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
  s.connect( ( sys.argv[1], 80 ) )
  s.close( )
except socket.error, e:
  if e[0] == 111:
    #if this is true then the vulnerable hosts web server is down so we consider
    #them not to be visible
    print "port 80 got connection refused!"
  elif e[0] == 110:
    print "connection to port 80 timed out... filtered?"
  else:
    print "got other socket error: %s" % ( e )
  sys.exit( 1 )
except Exception, e:
  print "Uknown exception: %s" % ( e )
  sys.exit( 1 )

#connection was not refused so return success
print "port 80 is open"
sys.exit( 0 )