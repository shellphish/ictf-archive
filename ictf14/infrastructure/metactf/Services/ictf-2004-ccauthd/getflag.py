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
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((ip,port))
    rtil_str(sock, "\n")
    sock.send("AUTH "+token+"\n")
    response=rtil_str(sock, "\n")
    authText=response.strip()
    authText=response.split()
    self.flag=authText[1]
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
