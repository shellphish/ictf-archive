#! /usr/bin/env python

# set flag example

import random
import string
import base64
import re
from socket import socket
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA

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

class SetFlag():

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
        

    def do_setflag(self, flag_id, token, flag):
        fcontent = token + "\n" + flag + "\n"
        full_command = "write" + "|" + flag_id + "|" + base64.b64encode(fcontent)
        
        signer = PKCS1_v1_5.new(private_key_rsa)
        digest = SHA.new() 
        digest.update(full_command)
        cert = signer.sign(digest)
        
        self.wait_for_regex("^what do you want to do?")
        self.send_msg(full_command)
        self.wait_for_regex("^give me the certificate!")
        self.send_msg(base64.b64encode(cert))
        self.wait_for_regex("^OK")
        self.wait_for_regex("^Bye")
    
    def get_random_flag_id(self):
        flag_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(16))
        return flag_id

    def get_random_token(self):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(16))
        flag_id = get_random_flag_id()

    def execute(self, ip, port, flag):        
        self.flag_id = self.get_random_flag_id()
        self.token = self.get_random_token()
        
        error = 0
        error_msg = ''
        connected = False
        try:
            s = socket()
            s.connect((ip, port))
            self.sock = s
            self.sock_file = s.makefile()
            connected = True  
            
            self.do_setflag(self.flag_id, self.token, flag)
        except BaseException, e:
            if ((not connected)):
                error = -42
            else:
                error = 42
            error_msg = str(type(e)) + ":" + str(e)

        self.error = error
        self.error_msg = error_msg


    def result(self):
        return {'FLAG_ID' : self.flag_id,
                'TOKEN' : self.token,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }

               
if __name__ == "__main__":
    FLAG_POSSIBILITIES = string.ascii_uppercase + string.digits + string.ascii_lowercase
    new_flag = ''.join(random.choice(FLAG_POSSIBILITIES) for x in range(13))
    new_flag =  "FLG" + new_flag
    print new_flag
    
    sf = SetFlag()
    import sys
    sf.execute(sys.argv[1],9899,new_flag)
    print repr(sf.result())
    
    
    
    
    
               
               
               
