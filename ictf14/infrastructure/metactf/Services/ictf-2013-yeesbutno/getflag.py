import socket
import string

DEBUG = True

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
    #s.flush()
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
    sendMessage(s, usname) #send usname
    sendMessage(s, pwd) # send pwd
    

def checkflag(s, choise):
    
    sendMessage(s, choise) #send choise
    
def rtil_str(s, st):
    buf = ""
    x = 0
    while True:
        curr = s.recv(1)
        if curr == "":
            break
        buf += curr
        if(curr == st[x]):
            x += 1
            if x == len(st):
                break
        else:
            x = 0
    return buf
    
class GetFlag():
    def __init__(self):
        self.flag_id = ''
        self.token = ''
        self.error = 0
        self.error_msg = ''
        self.flag = ''
        self.data = ''

    def execute(self,ip,port, flag_id, token):
        try:
            s = getSocket(ip, port)
        except Exception as e:
            print str(e)
            self.error = -1
            self.error_msg = str(e)
            return
        try:
            login(s, flag_id, token)
            rtil_str(s,'?>')
            checkflag(s, 's')
            try:
                s.settimeout(15)
                tmp = ''
                while (True):
                    tmp = recvMessage(s)
                    if len(tmp) == 0:
                        break
                    self.data += tmp
            except Exception as e:
                pass
            #checkflag(s, 's')
            closeSocket(s)
            print self.data
            print 'ENDENDNDN'
            self.flag = self.data#.split('?>')[-1]

        except Exception as e:
            print str(e)
            self.error = 1
            self.error_msg = str(e)

    def result(self):
        return {'FLAG' : self.flag,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg
                }
if __name__== "__main__":
    import sys
    try:
        b = GetFlag()
        b.execute(sys.argv[1], 3336, sys.argv[2], sys.argv[3])
        print b.result()
    except Exception, e:
        print "Error: %s" % str(e)
