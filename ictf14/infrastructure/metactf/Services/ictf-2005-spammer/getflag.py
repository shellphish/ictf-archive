import socket

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
  def execute(self,ip,port,flag_id,token):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((ip,port))
    s.send('login %s %s\n' % (flag_id,token))
    s.send('stat\n')
    received = rtil_str(s,"200 OK")
    while len(received.split("200 OK")) is not 3:
      received += rtil_str(s,"200 OK")
    s.close()
    self.flag="FLG"+received.split("FLG")[1][:13]
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
