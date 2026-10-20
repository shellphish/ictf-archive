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

class Benign():
    def create_user_pass(self, ul, pl):
        username = ''.join(random.choice(string.ascii_letters + string.digits) for i in xrange(ul))
        password = ''.join(random.choice(string.ascii_letters + string.digits) for i in xrange(pl))

        return (username, password)

    def make_random_content(self, l):
        content = ''.join(random.choice(string.ascii_letters + string.digits) for i in xrange(l))
        return content

    def read_header(self, s):
        buf = s.recv(1024)
        if "cookie,command:" not in buf:
            buf = s.recv(1024)
            if "cookie,command:" not in buf:
                raise Exception("Unexpected responsei: %s" % buf)


    def do_benign(self, s, username, password):
        
        buf = s.recv(1024)
        if "user|pass" not in buf:
            raise Exception("Unexpected response: %s" % buf)
        #username, password = self.create_user_pass(20, 20)
        s.send("%s|%s" % (username, password))
        print "reading after auth"
        buf = s.recv(1024)
        print "read after auth"
        token = buf.split("\n")[0]
        if "cookie,command:" not in buf:
            buf = s.recv(1024)
            if "cookie,command:" not in buf:
                raise Exception("Unexpected responsei: %s" % buf)
        content = self.make_random_content(200)

        self.set_value(s, token, content)

        self.read_header(s)

        c = self.read_value(s, token)
        if c != content:
            raise Exception("Failed to store and retrieve")
        return (username, password, content)

        
    def set_value(self, s, token, text):
        print "in set_value"
        command = "write %s" % text
        buf = "%s,%s" % (token, command)
        s.send(buf)
        print "sent ", text


    def read_value(self, s, token):
        print "in read_value"
        command = "retv secret"
        buf = "%s,%s" % (token, command)
        s.send(buf)
        content = s.recv(1024)

        print "received ", content
        return content        



         
    def execute(self, ip, port, flag_id, token):
        error = 0
        error_msg = ''
        self.flag_id = None
        self.token = None
        self.error = None
        self.error_msg = None
        
        try:
            tmpuser, tmppass = self.create_user_pass(21, 20)
            if len(flag_id) == 0:
                flag_id = tmpuser
            if len(token) == 0:
                token = tmppass
            s = socket.socket()
            s.connect((ip, port))
            s.settimeout(10)
            ans = self.do_benign(s, flag_id, token)
        except Exception as e:
            error = 42
            error_msg = str(e)
            print e

        if error == 0:
            self.flag_id = flag_id
            self.token = token
        self.error = error
        self.error_msg = error_msg

    def result(self):
        if self.error == 0:
            return {'FLAG_ID' : self.flag_id,
                'TOKEN' : self.token,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }
        else:
            return {
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }

def main():
    b = Benign()
    username, password = b.create_user_pass(20, 20)
    username = "A"*21
    b.execute("127.0.0.1", int(sys.argv[1]), username, password)

if __name__ == "__main__":
    main()
