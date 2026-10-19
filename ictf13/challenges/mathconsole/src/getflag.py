#! /usr/bin/env python

# set flag example

import random
import string
import base64
import re
import sys
import hashlib
from socket import socket
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA

old_data =''

class GetFlag():

    DEBUG = False

    def send_recv_msg(self, s, msg):
        s.send(msg + '\n')
        ans = s.recv(128).strip()
        return ans

    def get_msg(self, s):
        msg = s.recv(128).strip()
        return msg
        
    def send_msg(self, data):
        self.sock.sendall(data + "\n")             
        
    def recv_msg(self):
        data = self.sock_file.readline()
        if(len(data)==0):
            raise Exception("Exit")
        return data.strip()
        
    def wait_for_regex(self, regex, pdata=True):
        global old_data
        compiled_regex = re.compile(regex)
        while True:
            data = self.sock_file.readline()
            if(pdata):
                print "->" + repr(data) + "<-"
            if(len(data)==0):
                raise Exception("Connection closed last received message: " + old_data
                    + " waiting for:" + regex)
            elif (compiled_regex.match(data)):
                break;
            old_data = data

    def sha1(self,content):
        sha1_hash = hashlib.sha1()
        sha1_hash.update(content)
        hash = sha1_hash.digest()
        return hash
        
    def do_getflag(self, flag_id, token):
        full_command = "read_protected" + "|" + flag_id + "|" + token
        
        hash = self.sha1(full_command)
        cert = "X"*(256-len(hash)) + hash
        
        self.wait_for_regex("^what do you want to do?")
        self.send_msg(full_command)
        self.wait_for_regex("^give me the certificate!")
        self.send_msg(base64.b64encode(cert))
        self.wait_for_regex("^Result")
        nstr = self.recv_msg()
        original_str = base64.b64decode(nstr)
        flag = original_str.split("\n")[1]
        self.wait_for_regex("^Bye")
        return flag
    
    def get_random_flag_id(self):
        flag_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(16))
        return flag_id

    def get_random_token(self):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(16))
        flag_id = get_random_flag_id()

    def execute(self, ip, port, flag_id, token):
        error = 0
        error_msg = ''
        connected = False
        flag = ''
        try:
            s = socket()
            s.connect((ip, port))
            self.sock = s
            self.sock_file = s.makefile()
            connected = True            
            
            flag = self.do_getflag(flag_id, token)
        except BaseException, e:
            if ((not connected)):
                error = -42
            else:
                error = 42
            error_msg = str(type(e)) + ":" + str(e)

        self.flag = flag
        self.error = error
        self.error_msg = error_msg

    def result(self):
        return {'FLAG' : self.flag,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }
               
if __name__ == "__main__":
    
    gf = GetFlag()
    gf.execute(sys.argv[1],9899,sys.argv[2],sys.argv[3])
    print repr(gf.result())
    
    
    
