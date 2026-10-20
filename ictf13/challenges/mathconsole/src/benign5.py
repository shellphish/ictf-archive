#! /usr/bin/env python

import random
import re
import hashlib
import base64
import sys
import binascii
from socket import socket
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA
from ecdsa import SigningKey



private_key_ec_pem = '''
-----BEGIN EC PRIVATE KEY-----
MF8CAQEEGICtlZA9paKUXrSbNmKfacWEmKnsDmFZMaAKBggqhkjOPQMBAaE0AzIA
BGQmD0a+nWG0ISZZdaOOYd2tNwHyTf4v95Vv8gPu6NRbLSdyy/auNcEzbCFYZ193
XA==
-----END EC PRIVATE KEY-----
'''
private_key_ec = SigningKey.from_pem(private_key_ec_pem.strip())
old_data =''
max_num = 4000


class Benign(): #this will use power with l3

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
                
    def execute(self, ip, port, flag_id='', token=''):
        error = 0
        error_msg = ''
        connected = False
        try:
            s = socket()
            s.connect((ip, port))
            self.sock = s
            self.sock_file = s.makefile()
            connected = True            

            self.do_benign(s)
        except BaseException, e:
            if ((not connected)):
                error = -42
            else:
                error = 42
            error_msg = str(type(e)) + ":" + str(e)

        self.flag_id = ''
        self.token = ''
        self.error = error
        self.error_msg = error_msg

    def result(self):
        return {'FLAG_ID' : self.flag_id,
                'TOKEN' : self.token,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }

    def send_msg(self, data):
        self.sock.sendall(data + "\n")             
        
    def recv_msg(self):
        data = self.sock_file.readline()
        if(len(data)==0):
            raise Exception("Exit")
        return data.strip()
               
    def do_benign(self,s):
        random.seed()

        n1 = str(random.randint(1,max_num))
        n2 = str(random.randint(1,max_num))
        command =  "power"
        full_command = command + "|" + n1 + "|" + n2

        hash = self.sha1(full_command)
        cert_key = private_key_ec.sign_digest(hash,k=4) #this is vulnerable
        cert = "X"*(256-len(cert_key)) + cert_key
        
        print full_command
        self.wait_for_regex("^what do you want to do?")
        self.send_msg(full_command)
        self.wait_for_regex("^give me the certificate!")
        self.send_msg(base64.b64encode(cert))
        self.wait_for_regex("^Result")
        nstr = self.recv_msg()
        print nstr
        try:
            n = int(nstr)
        except ValueError:
            Exception("Invalid number returned")
        self.wait_for_regex("^Bye")
        
        
        
if __name__ == "__main__":
    b = Benign()
    b.execute("127.0.0.1",9899)
    print repr(b.result())
        

