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

    def get_flag(self, cookie, password):
        # Reads the flag
        flag = ""
        error = 42
        error_msg = "No valid response returned from server"

        message = "STATUS %s %s\n" % (cookie, password)
        if debug:
            print "Sending compound sms message: %s" % message
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip, self.PORT))
            smsfd = s.makefile()
            s.send(message)
            while True:
                response = smsfd.readline().strip()
                if "ERROR" in response:
                    flag = ""
                    error = 1
                    error_msg = response

                    break
                if response == "":
                    break
                print "Received reply: %s" % response
                if response.startswith('#PARSED '):
                    flag = response.replace('#PARSED ', '')
                    error = 0
                    error_msg = ""
                    break
            s.close()
        except Exception, err:
            error_msg = "Msg dispatcher is down: cannot read flag: %s" % str(err)
            error = 1
            flag = ""

        return flag, error, error_msg

class GetFlag():
  def execute(self, ip, port, flag_id, token):
    user = MsgUser(ip)
    flag, error, error_msg = user.get_flag(cookie=flag_id, password=token)

    self.flag = flag
    self.error = error
    self.error_msg = error_msg

  def result(self):
    return {'FLAG' : self.flag,
            'ERROR' : self.error,
            'ERROR_MSG' : self.error_msg,
           }

if __name__ == "__main__":
    import sys
    gf = GetFlag()
    gf.execute(sys.argv[1], 31337, sys.argv[2], sys.argv[3])

    print gf.result()

