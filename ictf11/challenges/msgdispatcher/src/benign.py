#!/usr/bin/env python
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

random.seed(os.urandom(20))

def get_random_string():
    return ''.join(random.choice(string.ascii_lowercase)
                for x in range(random.choice(range(10, 20))))

def get_random_email():
    tlds = ('com', 'org', 'info', 'biz')
    email = "%s@%s.%s" % (get_random_string(), get_random_string(), random.choice(tlds))
    return email


debug = 1

class MsgUser(object):

    # FIXME: add more
    bodies = ('How are you?', "How do you feel?", "See you in ten") # These should be random
    PORT = 31337

    def __init__(self, ip):
        self.ip = ip

    def set_flag(self, cookie, flag, password):
        print "Using cookie %s" % cookie
        print "Using password %s" % password

        username = get_random_email()

        msgtime = time.strftime("%Y-%m-%d %H:%M:%S")
        subject =  flag
        body = random.choice(self.bodies)
        group = get_random_string()
        message ="""SEND %s .oOo.
        <msg>
          <time>%s</time>
          <sender>%s</sender>
          <group>%s</group>
          <subject>%s</subject>
          <msgbody>%s</msgbody>
          <password>%s</password>
        </msg>
        .oOo.
        """ % (cookie, msgtime, username, group, subject, body, password)
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


class SetFlag():
  def execute(self, ip, port, flag):
    user = MsgUser(ip)
    cookie = get_random_string()
    flag_id = get_random_string()
    user.set_flag(cookie=cookie, flag=flag, password=flag_id)

    self.flag_id = flag_id
    self.token = cookie
    self.error = 0
    self.error_msg = ""

  def result(self):
    return {'FLAG_ID' : self.flag_id,
            'TOKEN' : self.token,
            'ERROR' : self.error,
            'ERROR_MSG' : self.error_msg,
           }

class GetFlag():
  def execute(self, ip, port, flag_id, token):
    user = MsgUser(ip)
    flag, error, error_msg = user.get_flag(cookie=token, password=flag_id)

    self.flag = flag
    self.error = error
    self.error_msg = error_msg

  def result(self):
    return {'FLAG' : self.flag,
            'ERROR' : self.error,
            'ERROR_MSG' : self.error_msg,
           }

class Benign(object):
    def __init__(self):
        self.flag_id = ''
        self.token = ''
        self.error = 2
        self.error_msg = 'Uninitialized'

    def result(self):
        return { 'FLAG_ID': self.flag_id,
                    'TOKEN': self.token,
                    'ERROR': self.error,
                    'ERROR_MSG': self.error_msg,
                }

    def execute(self, ip, port, flag_id, token):
        error, error_msg = 0, ''

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            self.do_benign(s, flag_id, token)

        except Exception as ex:
            error = 42
            error_msg = str(ex)

        self.flag_id = flag_id
        self.token = token
        self.error = error
        self.error_msg = error_msg

    def do_benign(self, s, flag_id, token):
        # We either generate random garbage and directly pipe it to the remote server,
        # or actually call set_flag() or get_flag() functions

        choice = random.randint(0, 2)
        if choice in (0, 1, 2):
            # Send garbage to the remote side
            error, error_msg = self.send_garbage(s)
        # TODO: implement other logics as well

    def send_garbage(self, s):
        length = random.randint(10, 5000)
        x = "".join([ chr(random.randint(1, 255)) for i in xrange(length) ])

        s.sendall(x)

        return 0, ''

if __name__ == "__main__":
    import sys
    be = Benign()
    be.execute(sys.argv[1], 31337, sys.argv[2], sys.argv[3])

    print be.result()

