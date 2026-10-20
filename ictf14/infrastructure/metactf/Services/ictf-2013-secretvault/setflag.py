import socket
import sys
import Crypto.Cipher.AES
import base64
import multiprocessing
import datetime
import os
from multiprocessing import Lock, Manager
import pexpect
import string
import random
class SetFlag():

    DEBUG = False
    
    def create_user_pass(self, ul, pl):
        username = ''.join(random.choice(string.ascii_letters + string.digits) for i in xrange(ul))
        password = ''.join(random.choice(string.ascii_letters + string.digits) for i in xrange(pl))

        return (username, password)

    def make_random_content(self, l):
        content = ''.join(random.choice(string.ascii_letters + string.digits) for i in xrange(l))
        return content

    def do_setflag(self, s, flag):
        
        buf = s.recv(1024)
        if "user|pass" not in buf:
            raise Exception("Unexpected response: %s" % buf)
        username, password = self.create_user_pass(20, 20)
        s.send("%s|%s" % (username, password))
        buf = s.recv(1024)
        token = buf.split("\n")[0]
        if "cookie,command:" not in buf:
            buf = s.recv(1024)
            if "cookie,command:" not in buf:
                raise Exception("Unexpected responsei: %s" % buf)
        #content = self.make_random_content(200)

        self.set_value(s, token, flag)
        print "wrote", flag

        buf = s.recv(1024)
        #token = buf.split("\n")[0]
        if "cookie,command:" not in buf:
            buf = s.recv(1024)
            if "cookie,command:" not in buf:
                raise Exception("Unexpected responsei: %s" % buf)
        c = self.read_value(s, token)
        print "read", c
        if c != flag:
            raise Exception("Failed to store and retrieve")
        return (username, password, flag)

        
    def set_value(self, s, token, text):
        command = "write %s" % text
        buf = "%s,%s" % (token, command)
        s.send(buf)
        print "sent ", text


    def read_value(self, s, token):
        command = "retv secret"
        buf = "%s,%s" % (token, command)
        s.send(buf)
        content = s.recv(1024)

        print "received ", content
        return content        



         
    def execute(self, ip, port, flag):
        error = 0
        error_msg = ''
        self.flag_id = None
        self.token = None
        self.error = None
        self.error_msg = None
        try:
            try:
                connect_success = False
                s = socket.socket()

                s.connect((ip, port))
                s.settimeout(10)
                connect_success = True
            except Exception, e:
                error = -1
                error_msg = "cannot connect"
            if connect_success:
                ans = self.do_setflag(s, flag)
        except Exception as e:
            error = 42
            error_msg = str(e)
            print e

        
        if error == 0:
            self.flag_id = ans[0]
            self.token = ans[1]
        self.error = error
        self.error_msg = error_msg

    def result(self):
        return {'FLAG_ID' : self.flag_id,
                'TOKEN' : self.token,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }
if __name__== "__main__":
    try:
        b = SetFlag()
        b.execute(sys.argv[1], 2190, sys.argv[2])
        print b.result()
    except Exception, e:
        print "Error: %s" % str(e)
