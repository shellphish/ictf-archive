import sys
import os
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

class Benign():

    def __init__(self):
        self.error = 0
        self.error_msg = ''
        self.flag_id = ''
        self.token = ''

    def makeCredentials(self):
        if (DEBUG):
            print "function makeCredential()"
        a = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        nameLength = random.randint(5,20)
        pwdLength = random.randint(5,30)
        secretLength = random.randint(5,20)
        name = ''
        pwd = ''
        flag = ''
        for i in range(1,nameLength):
            name += a[random.randint(0,len(a)-1)]
        for i in range(1,pwdLength):
            pwd += a[random.randint(0,len(a)-1)]
        for i in range(1,secretLength):
            flag += a[random.randint(0,len(a)-1)]
        if (DEBUG):
            print name
        if (DEBUG):
            print pwd
        if (DEBUG):
            print flag
        return name,pwd,flag


    def makeDirection(self):
        if (DEBUG):
            print "FUNCTION makeDirection()"
        a = ['n','s','e','w']
        pos = random.randint(0,3)
        return a[pos]


    def reg_success(self, s):
        if (DEBUG):
            print ("\n\nBenign traffic: branch reg_success\n\n")
        cr = self.makeCredentials()
        name = cr[0]
        pwd = cr[1]
        flag = cr[2]
        try:
            register(s, name, pwd, flag) #register and logging in
            self.flag_id = name
            self.token = pwd
        except Exception as e:
            print str(e)
            self.error = 1
            self.error_msg = str(e)
        if (DEBUG):
            print ("\n\nBenign traffic: branch reg_success END\n\n")

    def log_try(self, s, flag_id, token):
        if (DEBUG):
            print ("\n\nBenign traffic: branch log_try\n\n")
        if (flag_id == '' or token == ''):
            cr = self.makeCredentials()
            flag_id = cr[0]
            token = cr[1]
        login(s,flag_id, token) # login
        if (DEBUG):
            print ("\n\nBenign traffic: branch log_try END\n\n")


    def reg_play_success(self,s):
        if (DEBUG):
            print ("\n\nBenign traffic: branch reg_play_success\n\n")
        cr = self.makeCredentials()
        name = cr[0]
        pwd = cr[1]
        flag = cr[2]
        try:
            register(s, name, pwd, flag) #register and logging in
            data = recvMessage(s) #question play or secret
            sendMessage(s,'p')
            for i in range(5,15):
                data = recvMessage(s) #game
                d = self.makeDirection()
                sendMessage(s,d)
        except Exception as e:
            print str(e)
            self.error = 1
            self.error_msg = str(e)
        if (DEBUG):
            print ("\n\nBenign traffic: branch reg_play_success END\n\n")

    def reg_play_fail(self,s):
        if (DEBUG):
            print ("\n\nBenign traffic: branch reg_play_fail\n\n")
        cr = self.makeCredentials()
        name = cr[0]
        pwd = cr[1]
        flag = cr[2]
        try:
            register(s, name, pwd, flag) #register and logging in
            data = recvMessage(s) #question play or secret
            sendMessage(s,'p')
            for i in range(1,5):
                data = recvMessage(s) #game
                d = self.makeDirection()
                sendMessage(s,d)

            data = recvMessage(s) #game
            if (DEBUG):
                print "FATTO"
            sendMessage(s,'ciaociao')
        except Exception as e:
            print str(e)
            self.error = 1
            self.error_msg = str(e)
        if (DEBUG):
            print ("\n\nBenign traffic: branch reg_play_fail END\n\n")


    def execute(self,ip,port,flag_id="empty", token="empty"):
        self.flag_id = flag_id
        self.token = token
        branch = random.randint(0, 3)
        if (DEBUG):

            print ("branch", branch)

        try:
            s = getSocket(ip, port)
        except Exception as e:
            self.flag_id = ''
            self.token = ''
            self.error = -1
            self.error_msg = "connection refused"
            return

        try:
            if (branch==0):
                self.reg_play_fail(s)
            elif (branch==1):
                self.reg_play_success(s)
            elif (branch==2):
                self.log_try(s, flag_id, token)
            elif (branch==3):
                self.reg_success(s)

            closeSocket(s)
        except Exception as e:
            self.flag_id = ''
            self.token = ''
            self.error = 1
            self.error_msg = str(e)

    def result(self):
        return {'FLAG_ID' : self.flag_id,
                'TOKEN' : self.token,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg
                }
