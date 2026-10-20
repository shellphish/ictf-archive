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

class SetFlag():
  def execute(self,ip,port,flag):
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((ip,port))
    rtil_str(sock, "\n")
    sock.send("REG "+flag+"\n")
    response=rtil_str(sock, "\r\n")
    regText=response.strip()
    regText=regText.split()
    self.token=regText[1]
    self.flag_id=self.token[0:16];self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
