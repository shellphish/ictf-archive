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
import glob



def get_random_string():
    return ''.join(random.choice(string.ascii_lowercase)
                for x in range(random.choice(range(10, 20))))

def get_random_email():
    tlds = ('com', 'org', 'info', 'biz')
    email = "%s@%s.%s" % (get_random_string(), get_random_string(), random.choice(tlds))
    return email


debug = 1


class MsgUser(object):

    PORT = 31337

    def __init__(self, ip):
        self.ip = ip

    def get_flag(self, cookie):
        # Reads the flag
        message = "STATUS %s\n" % cookie
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
                if response.startswith('PARSED '):
                    return response.replace('PARSED ', '')
            s.close()
        except Exception, err:
            print "Msg dispatcher is down: cannot read flag: %s" % str(err)

    def set_flag(self, cookie, flag):
        print "Using cookie %s" % cookie

        username = get_random_email()

        msgtime = time.strftime("%Y-%m-%d %H:%M:%S")
        subject =  flag
        body = get_random_string()
        group = get_random_string()
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
        except Exception, err:
            print "Msg dispatcher is down: cannot set flag", err
        return cookie


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
        cookie = get_random_string()
        user.set_flag(cookie=cookie, flag=sys.argv[3])
        print 'COOKIE:%s' % cookie
    elif sys.argv[1] == 'get':
        flag = user.get_flag(cookie=sys.argv[3])
        print 'FLAG:%s' % flag
    elif sys.argv[1] == 'test':
        cookie = get_random_string()
        user.set_flag(cookie=cookie, flag="FLAG!")
        flag = user.get_flag(cookie=cookie)
        print 'FLAG:%s' % flag
    else:
        usage()

