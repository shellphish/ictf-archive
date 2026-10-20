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
    password = get_random_string()
    user.set_flag(cookie=cookie, flag=flag, password=password)

    self.flag_id = cookie
    self.token = password
    self.error = 0
    self.error_msg = ""

  def result(self):
    return {'FLAG_ID' : self.flag_id,
            'TOKEN' : self.token,
            'ERROR' : self.error,
            'ERROR_MSG' : self.error_msg,
           }

if __name__ == "__main__":
    import sys
    sf = SetFlag()
    sf.execute(sys.argv[1], 31337, sys.argv[2])

    print sf.result()

