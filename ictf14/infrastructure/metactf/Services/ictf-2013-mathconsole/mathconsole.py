#! /usr/bin/env python

import SocketServer
import threading
import base64
import sys
import shutil
import os
import re
import base64
import hashlib
import time
import random
import ctypes
from Crypto.PublicKey import RSA
from ecdsa import VerifyingKey,BadSignatureError





save_folder = "service_files"
service_name = "Math Console"
service_port = 9899
service_host = '0.0.0.0'
max_n_files = 25000
max_num = 4000

public_key_rsa_pem = '''
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqTPZJL6DgTTW2VKVGUfC
Ef+/5DGC0CmPfm0XHEGgA9nO/OKaT7ViDExJZTxNaJqiiRIXJf+O8D4iQw6Hcsag
V3GtriCrKUg9FNlmv28EII6YWzW+QLVAtEAqfMqf4049+XhjI2LGPmKrOgtMuyQ9
3bm04suEesHTo8dXfO2t+ECoPLlFHMaT9n1CSjPigs3gu+WkUN9VxHVRAXfC+7dx
yYfGtvUR+9yxJO/FYtHxrF1EKKhj/Lt4g3Z/njk8u/UrjnHnF0sd6xiODVSJWL9G
g6KfoIzTzBWTGzd5R7M8r34GKrBmPnAkBaKWlsTo8ItbjkPx9ECueCNUYC0LCAxb
TwIDAQAB
-----END PUBLIC KEY-----
'''
public_key_rsa = RSA.importKey(public_key_rsa_pem.strip())
public_key_ec_pem = '''
-----BEGIN PUBLIC KEY-----
MEkwEwYHKoZIzj0CAQYIKoZIzj0DAQEDMgAEZCYPRr6dYbQhJll1o45h3a03AfJN
/i/3lW/yA+7o1FstJ3LL9q41wTNsIVhnX3dc
-----END PUBLIC KEY-----
'''
public_key_ec = VerifyingKey.from_pem(public_key_ec_pem.strip())

commands = (
"sum", #b1
"multiply", #b1
"mod", #b1
"power", #b2
"write", #sf #b3
"read_encrypted1", #b4-b3-exp
"read_encrypted2", #b4 #!(exp2)
"read_protected" #gf
)
security_levels = (
    set((1,2)), #b1 sum
    set((1,)), #b1 multiply
    set((1,2)), #b1 mod
    set((3,)), #b2 power
    set((2,)), #sf #b3 write
    set((2,)), #b4-b3-exp read_encrypted1
    set((2,)), #b4 #!(exp2) read_encrypted2
    set((1,)) #gf read_protected
)
access_summary = 1

vvvvv = [72781, 16949, 52841, 88733, 28913, 66799, 30907, 12961,
     82751, 18943, 60817, 42871, 22931, 40877, 4985, 36889, 58823,
     74775, 70787, 1994, 10967, 6979, 96709, 46859, 2991]

vvvvvvvvoooooooo0=123
vvvvvvvvoooooooo1=123
vvvvvvvvoooooooo2=123
vvvvvvvvoooooooo3=123
vvvvvvvvoooooooo4=123
vvvvvvvvoooooooo5=123
vvvvvvvvoooooooo6=123
vvvvvvvvoooooooo7=123
vvvvvvvvoooooooo8=123
vvvvvvvvoooooooo9=123

primes = [p/997 for p in  sorted(vvvvv)] #75 is not prime :-) (79) 


#uncompyle trick
fff=False
if(fff):
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0
    a = 0/0


def init_access():
    global access_summary
    for i,s in enumerate(security_levels):
        for e in s:
            access_summary *= (primes[((i*3)+e)]**2)
    

class MyTCPHandler(SocketServer.StreamRequestHandler):
    #This is instantiated once per connection to the server, and must override the handle() method to implement communication to the client.
    
    def sha1(self,content):
        sha1_hash = hashlib.sha1()
        sha1_hash.update(content)
        hash = sha1_hash.digest()
        return hash
    
    def recv_msg(self):
        data = self.rfile.readline()
        if(len(data)==0):
            sys.exit(1)
            
        return data.strip()

    def send_msg(self, data):
        self.wfile.write(data + "\n")
        
    def ask_question(self,question,options):
        option_str = "/".join(options)
        tstr = question + " [%s]" % option_str
        self.send_msg(tstr)
        rmesg = self.recv_msg()
        while(rmesg not in options):
            self.send_msg("Invalid input, valid options: [%s]" % option_str)
            rmesg = self.recv_msg()
        return rmesg
        
    def ask_regex(self,question,regex):
        compiled_regex = re.compile(regex)
        self.send_msg(question)
        rmesg = self.recv_msg()
        while(not compiled_regex.match(rmesg)):
            self.send_msg("Invalid input")
            rmesg = self.recv_msg()
        return rmesg
    
    def terminate(self,msg=""):
        if(msg!=""):
            self.send_msg(msg)
        raise(SystemExit)
    
    def handle(self):
        print "* start handling a connection *"
        try:
            self.internal_handle()
        except KeyboardInterrupt:
            pass
        except SystemExit:
            pass
        print "* stop handling a connection *"
    
    def string_to_hexstring(self,string):
        res = "".join("{0:02x}".format(ord(c)) for c in string)
        return res
        
    def verify_with_pubkey_rsa(self,public_key_rsa,local_hash,certificate):
        '''
        uiii
        '''
        #http://wiibrew.org/wiki/Signing_bug
        m = public_key_rsa.encrypt(certificate,None)[0]
        m = "\x00"*(256-len(m)) + m #this is not strictly necessary
        remote_hash = m[-20:] #the padding is not checked
        libc = ctypes.CDLL("libc.so.6")
        if(libc.memcmp(local_hash,remote_hash,20)==0): #strncmp was REALLY bad here
            return True
        else:
            return False
            
    def verify_with_pubkey_ec(self,public_key_ec,local_hash,certificate):
        '''
        p$p$p$
        '''
        #http://kakaroto.homelinux.net/2012/01/how-the-ecdsa-algorithm-works/
        #http://en.wikipedia.org/wiki/Elliptic_Curve_DSA
        try:
            public_key_ec.verify_digest(certificate[-48:],local_hash)
            return True
        except BadSignatureError:
            return False        
        
    def check_l1_certificate(self,hash,certificate):
        if(hash == certificate[-20:]):
            return 1
        else:
            return 0   
    def check_l2_certificate(self,hash,certificate):
        if(self.verify_with_pubkey_rsa(public_key_rsa,hash,certificate)):
            return 1
        else:
            return 0
    def check_l3_certificate(self,hash,certificate):
        if(self.verify_with_pubkey_ec(public_key_ec,hash,certificate)):
            return 1
        else:
            return 0
    
    def check_security_level(self,cmd,auth_info):
        idx = commands.index(cmd)
        for i in xrange(0,3):
            if(auth_info[i]==0):
                continue
            l = i+1
            p = primes[(idx*3)+l]
            #print "->",p,access_summary
            if(access_summary%p == 0):
                return
        else:
            self.terminate("invalid certificate level!")
    
    def p2pv(self,p1,p2):
        try:
            p1v = int(p1)
            p2v = int(p2)
        except ValueError:
            self.terminate("invalid number")
        if(p1v<0 or p1v > max_num or p2v < 0 or p2v > max_num):
            self.terminate("invalid number")
        return p1v,p2v
        
    def p2xk(self,p):
        try:
            pv = int(p)
        except ValueError:
            self.terminate("invalid number")
        return (pv%256)
        
    def parse_command(self,line_command):
        if(line_command.count("|")!=2):
            self.terminate("Invalid command format!")
        return line_command.split("|")
    
    def check_file_name(self,fname):
        #partially already checked when the whole command is validated
        compiled_regex = re.compile("^[a-zA-Z0-9_]{1,50}$") 
        if(not(compiled_regex.match(fname))):
            self.terminate("invalid file name")
            
    def decode_file_content(self,fcontent):
        content = ""
        try:
            content = base64.b64decode(fcontent)
        except TypeError:
            self.terminate("invalid file content")
        return content
        
    def ror(self,x):
        mask = (2L**1) - 1
        mask_bits = x & mask
        return (x >> 1) | (mask_bits << (8 - 1))
            
    def exec_command(self,line_command,auth_info):
        c,p1,p2 = self.parse_command(line_command)
        
        res = ""
        if(c=="sum"):
            self.check_security_level(c,auth_info)
            p1v,p2v = self.p2pv(p1,p2)
            res = str(p1v+p2v)
        elif(c=="multiply"):
            self.check_security_level(c,auth_info)
            p1v,p2v = self.p2pv(p1,p2)
            res = str(p1v*p2v)
        elif(c=="mod"):
            self.check_security_level(c,auth_info)
            p1v,p2v = self.p2pv(p1,p2)
            res = str(p1v%p2v)
        elif(c=="power"):
            self.check_security_level(c,auth_info)
            p1v,p2v = self.p2pv(p1,p2)
            res = str(p1v**p2v)
        elif(c=="write"):
            self.check_security_level(c,auth_info)
            self.check_file_name(p1)
            c = self.decode_file_content(p2)
            
            if(os.path.isfile(os.path.join(save_folder,p1))):
                self.terminate("already existing file")
            n_files = (len([name for name in os.listdir(os.path.join(save_folder,".")) 
                    if os.path.isfile(os.path.join(save_folder,name))]))
            if(n_files >= max_n_files):
                clean_save_folder()
                
            fp = open(os.path.join(save_folder,p1),"wb")
            fp.write(c)
            fp.close()
            res = "OK"
        elif(c=="read_encrypted1"):
            self.check_security_level(c,auth_info)
            self.check_file_name(p1)
            try:
                fp = open(os.path.join(save_folder,p1),"rb")
                c = fp.read()
                fp.close()
            except IOError:
                self.terminate("error reading file")
            xk = self.p2xk(p2)
            nc = ""
            for i in c:
                nc += chr(ord(i) ^ xk)
            res = base64.b64encode(nc)
        elif(c=="read_encrypted2"):
            self.check_security_level(c,auth_info)
            self.check_file_name(p1)
            try:
                fp = open(os.path.join(save_folder,p1),"rb")
                c = fp.read()
                fp.close()
            except IOError:
                self.terminate("error reading file")
            xk = self.p2xk(p2)
            nc = ""
            for i in c:
                nc += chr(ord(i) ^ xk)
                xk=self.ror(xk)
            res = base64.b64encode(nc)
        elif(c=="read_protected"): #only getflag is able to use this
            self.check_security_level(c,auth_info)
            self.check_file_name(p1)
            try:
                fp = open(os.path.join(save_folder,p1),"rb")
                c = fp.read()
                fp.close()
            except IOError:
                self.terminate("error reading file")
            saved_password = c.split("\n")[0]
            if(saved_password!=p2): #this password is the cookie
                self.terminate("wrong password!")
            else:
                res = base64.b64encode(c)

        else:
            self.terminate("Invalid command!")
            
        self.send_msg("Result:")
        self.send_msg(res)
        print "res:",res
        self.send_msg("Bye")

    def validate_certificate(self,line_command,certificate):
        hash = self.sha1(line_command)
        
        l1_certificate = self.check_l1_certificate(hash,certificate)
        l2_certificate = self.check_l2_certificate(hash,certificate)
        l3_certificate = self.check_l3_certificate(hash,certificate)
        certificate_comments = certificate[:32]
        auth_info = (l1_certificate,l2_certificate,l3_certificate,certificate_comments) 
        return auth_info

    def internal_handle(self):
        self.send_msg("Welcome to the most powerful backdoor-free calculator")
        self.send_msg("You can use it to safely perform your calculations about Nuclear reactions and trajectories of missiles")
        self.send_msg("A new on-the-cloud hacker-proof file storage functionality has been just added")
        self.send_msg("Wii fixed it! :-)")

        self.send_msg("available commands:");
        self.send_msg("sum|<n1>|<n2> required authorization: L1 or L2");
        self.send_msg("multiply|<n1>|<n2> required authorization: L1");
        self.send_msg("mod|<n1>|<n2> required authorization: L1 or L2");
        self.send_msg("power|<n1>|<n2> required authorization: L3");
        self.send_msg("write|<fname>|<b64 content> required authorization: L2");
        self.send_msg("read_encrypted1|<fname>|<key> required authorization: L2");
        self.send_msg("read_encrypted2|<fname>|<key> required authorization: L2"); #or L3
        self.send_msg("read_protected|<fname>|<password> required authorization: L1 + password");
        line_command = self.ask_regex("what do you want to do?",r"^[a-zA-Z0-9_+/=|]{1,200}$");

        certificate_b64 = self.ask_regex("give me the certificate!",
                r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$")
        certificate = base64.b64decode(certificate_b64)
        if(len(certificate)!=256):
            self.terminate("invalid certificate!")
            
        auth_info = self.validate_certificate(line_command,certificate)
        print "command:", line_command
        print "certificate_b64:", certificate_b64
        print "auth_info:", repr(auth_info)
        self.exec_command(line_command,auth_info)
        
class ForkingTCPServer(SocketServer.ForkingMixIn, SocketServer.TCPServer):
    pass

def clean_save_folder():
    if(os.path.isdir(save_folder)):
        try:
            shutil.rmtree(save_folder)
        except OSError, e:
            pass
    try:
        os.mkdir(save_folder)
    except OSError, e:
        pass
        
    
if __name__ == "__main__":
    #print max_n_files
    if(len(sys.argv) == 2):
        service_port = int(sys.argv[1])
    
    clean_save_folder()
    init_access()

    # Prevent 'cannot bind to address' errors on restart
    ForkingTCPServer.allow_reuse_address = True
    server = ForkingTCPServer((service_host, service_port), MyTCPHandler)

    ip, port = server.server_address

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
        print "*** " + service_name + " service started! ***"
        server.serve_forever()
    except KeyboardInterrupt:
        print "*** " + service_name + " service shutting down ***"
        server.shutdown()
   
   
