import random
import math

import socket

DEBUG = False

#create and connect to the socket
def getSocket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
    return s

def recvMessage(s):
    data = s.recv(1024)
    if (DEBUG):
        print data
    return data

def sendMessage(s,mess):
    s.sendall(mess+'\n')
    if (DEBUG):
        print mess

def closeSocket(s):
    try:
        s.close()
    except Exception as e:
        print e.message
        pass

def register(s, usname, pwd, secret):
    if (DEBUG):
        print "registration"
    data = recvMessage(s) #receive tic and usname
    tic = data.split(': ')[1]
    tic = tic.split('.')[0]
    sendMessage(s, usname) #send usname
    data = recvMessage(s) #receive pwd
    sendMessage(s, pwd) # send pwd
    data = recvMessage(s) #receive secret
    sendMessage(s, secret) #send secret
    return tic

def login(s, usname, pwd):
    if (DEBUG):
        print "login"
    data = recvMessage(s) #receive usname
    sendMessage(s, usname) #send usname
    data = recvMessage(s) #receive pwd
    sendMessage(s, pwd) # send pwd
    #data = recvMessage(s) #receive secret
    #sendMessage(s, '') # send empty string in order to log in
    if (DEBUG):
        print "logged"

class SetFlag():
    def __init__(self):
        self.flag_id = ''
        self.token = ''
        self.error = 0
        self.error_msg = ''

    def execute(self,ip,port, flag):
        a = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        nameLength = random.randint(5,20)
        pwdLength = random.randint(5,20)
        name = ''
        pwd = ''
        for i in range(1,nameLength):
            name += a[random.randint(0,len(a)-1)]
        for i in range(1,pwdLength):
            pwd += a[random.randint(0,len(a)-1)]
        try:
            s = getSocket(ip, port)
        except Exception as e:
            print str(e)
            self.error = -1
            self.error_msg = str(e)
            return
        try:
            register(s, name, pwd, flag) #register and logging in
            self.flag_id = name
            self.token = pwd
        except Exception as e:
            print str(e)
            self.error = 1
            self.error_msg = str(e)
        closeSocket(s)
    def result(self):
        return {'FLAG_ID' : self.flag_id,
                'TOKEN' : self.token,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg
                }
if __name__== "__main__":
    import sys
    try:
        b = SetFlag()
        b.execute(sys.argv[1], 3336, sys.argv[2])
        print b.result()
    except Exception, e:
        print "Error: %s" % str(e)
