#! /usr/bin/env python

import string
import random
import re
import hashlib
import base64
import sys
import binascii
import time
from socket import socket
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA
from ecdsa import SigningKey



private_key_rsa_pem = '''
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAqTPZJL6DgTTW2VKVGUfCEf+/5DGC0CmPfm0XHEGgA9nO/OKa
T7ViDExJZTxNaJqiiRIXJf+O8D4iQw6HcsagV3GtriCrKUg9FNlmv28EII6YWzW+
QLVAtEAqfMqf4049+XhjI2LGPmKrOgtMuyQ93bm04suEesHTo8dXfO2t+ECoPLlF
HMaT9n1CSjPigs3gu+WkUN9VxHVRAXfC+7dxyYfGtvUR+9yxJO/FYtHxrF1EKKhj
/Lt4g3Z/njk8u/UrjnHnF0sd6xiODVSJWL9Gg6KfoIzTzBWTGzd5R7M8r34GKrBm
PnAkBaKWlsTo8ItbjkPx9ECueCNUYC0LCAxbTwIDAQABAoIBAGhIlGSZJuPTdTes
NkjGeU4umk5CVaWGd/IrujqoF79H1tL1trW5zRxXSEUkzXDTHanthGbfA3H+WY+K
vOB4mwpJ/gl8CQIAi+T1uOXzvk9yk2Rj00Z+b8qoYYdYOwMVjgzbrf55OkXo+i9k
F36f76Fge6PsW1Jtc8tVaQ6OTtLZxaPwAC5Fd1A0mHoZWUr9oaeW0xk6dMAB/bcg
9RvCfowZm/E0yx6PX1CcCc1Ig7fyLcnE3VHB1Jtayzm0aQZ4ujVddhfFC2zb7y4A
VfxStFvP2KCeuKOOrC3SBxoWo0NSgw8QrkFFzxhi0YX0f646BNiXOQufN3MDKFSc
9oz54UECgYEA330K0VjtDiX3aZsSOixZGiymzcglipeMSGXhmdKBt81q0CVMtKzM
2A6J8Ay4zUK//EY+yWrAdlO9nTVgZV4aui2tFAVi4pXovnL/ZezKFYaBi0XoO4z0
7LOlJdb59xd76vR895TLcOG5uylRJEugXI7IYmrMfcFQqGpoDk5PIZUCgYEAwdEj
Ze8dRwIV8LnEfpTg5Vqc0xYAB8ACC3CmQezGNzr754sCypp+ChEaeSZSOkM+1dP+
+x4hGNFeFYpdNbTzO34gxywZzJXJXXU4kTcR74pchq/HEJnw8Kf51JsTPGdy4Vl3
cS95S6qqlOUFzt50iL3l0vQ7owkY+cpve1GkmFMCgYAXk9eKUnlf3r2FVKjNnlQg
IMnQN+dOAcL4+FaepcitnWxBXU4EWZ6axJ3kx1LPxNUARmDlWu/HC/qbFUCAMTdc
oOj7jb3q7anKPdOX6y0+rBwKl2tyrOJB/onTviRM3xthpD1y2S3FUOsJRcibrabT
XPTi/SVptvVNbzxfFf/fKQKBgEU5HAp5J5zH6uwqfTq0k8p23ZIqxmH+Ovy5BDiB
h54MTBI7vQh9u0x/JVRl0nKKt/OJHwWzkiCaDp9k5rua4FC8UJqybph6WwwtJMIA
yEAky70zJMcSJFLfu8QqiulFDWvdF2LukMTstLYvQi7LlxWLtXztzCsDwc7ddYm2
9DGPAoGAII1brW87NHjboBKR7qd2McCSQhMhiuOlAuf6ETv5Dv5SxdDcx/Ibac/v
D4LSenMAVqzpYdHL6P/sITQ/5GekvMRLJSCVTJiUl8jABezH05DdC9Q9Tu9IiVHJ
uOJR3LgJOmfmZO3DeCh0nQzndwfE49qYc6w1aQl8zX6I8LDL+/4=
-----END RSA PRIVATE KEY-----
'''
private_key_rsa = RSA.importKey(private_key_rsa_pem.strip())
old_data =''
max_num=4000

class Benign(): #this will use read_encrypted1 and read_encrypted2 with l2 on the same file, given a flag id

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
        if(flag_id==''): #without flagid, do as in benign1
            error = 0
            error_msg = ''
            connected = False
            try:
                s = socket()
                s.connect((ip, port))
                self.sock = s
                self.sock_file = s.makefile()
                connected = True            

                self.do_benign_base(s)
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
            return
        
        
        error = 0
        error_msg = ''
        connected = False
        try:
            s = socket()
            s.connect((ip, port))
            self.sock = s
            self.sock_file = s.makefile()
            connected = True                        

            fcontent = self.do_benign_read1(flag_id)
            s.close()

            #time.sleep(20)
            s = socket()
            s.connect((ip, port))
            self.sock = s
            self.sock_file = s.makefile()
            self.do_benign_read2(fcontent,flag_id)
            
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
        
    def ror(self,x):
        mask = (2L**1) - 1
        mask_bits = x & mask
        return (x >> 1) | (mask_bits << (8 - 1))
        
    def recv_msg(self):
        data = self.sock_file.readline()
        if(len(data)==0):
            raise Exception("Exit")
        return data.strip()
               
    def unxor(self,tstr,x):
        nc = ""
        for i in tstr:
            nc += chr(ord(i) ^ x)
        return nc
        
    def unxorr(self,tstr,x):
        nc = ""
        for i in tstr:
            nc += chr(ord(i) ^ x)
            x = self.ror(x)
        return nc
        
    def do_benign_base(self,s):
        random.seed()
        
        methods = ["l1","l2"]
        commands = ["sum","multiply","mod"]
        n1 = str(random.randint(1,max_num))
        n2 = str(random.randint(1,max_num))
        
        command = random.choice(commands)
        
        if(command == "multiply"):
            method = "l1" #random.choice(methods)#"l1"
        else:
            method = random.choice(methods)
            
        full_command = command + "|" + n1 + "|" + n2
        
        if(method == "l1"):
            print "l1"
            hash = self.sha1(full_command)
            cert = "X"*(256-len(hash)) + hash
        else:
            print "l2"
            signer = PKCS1_v1_5.new(private_key_rsa)
            digest = SHA.new() 
            digest.update(full_command)
            cert = signer.sign(digest)
        
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

    def do_benign_read1(self,flag_id):
        key = random.randint(0,max_num)
        command = "read_encrypted1" + "|" + flag_id + "|" + str(key)

        hash = self.sha1(command)
        signer = PKCS1_v1_5.new(private_key_rsa)
        digest = SHA.new() 
        digest.update(command)
        cert = signer.sign(digest)
        
        self.wait_for_regex("^what do you want to do?")
        self.send_msg(command)
        if(flag_id==""):
            return ""
        self.wait_for_regex("^give me the certificate!")
        self.send_msg(base64.b64encode(cert))
        self.wait_for_regex("^Result")
        nstr = self.recv_msg()
        original_str = base64.b64decode(nstr)
        unxor_str = self.unxor(original_str,key%256)
        self.wait_for_regex("^Bye")  
        return unxor_str
        
    def do_benign_read2(self,fcontent,flag_id):
        key = random.randint(0,max_num)
        command = "read_encrypted2" + "|" + flag_id + "|" + str(key)

        hash = self.sha1(command)
        signer = PKCS1_v1_5.new(private_key_rsa)
        digest = SHA.new() 
        digest.update(command)
        cert = signer.sign(digest)
        
        self.wait_for_regex("^what do you want to do?")
        self.send_msg(command)
        if(flag_id==""):
            return ""
        self.wait_for_regex("^give me the certificate!")
        self.send_msg(base64.b64encode(cert))
        self.wait_for_regex("^Result")
        nstr = self.recv_msg()
        original_str = base64.b64decode(nstr)
        unxorr_str = self.unxorr(original_str,key%256)
        print unxorr_str
        self.wait_for_regex("^Bye")  
        
        if(unxorr_str!=fcontent):
            raise Exception("unmatching file content between read_encrypted1 and read_encrypted2")
        
if __name__ == "__main__":
    b = Benign()
    b.execute("127.0.0.1",9899,sys.argv[1])
    print repr(b.result())
        

