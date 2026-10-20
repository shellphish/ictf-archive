import socket, string, random

class Benign():
  def execute(self, ip, port, flag_id, token):
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    flag=''.join(random.choice(string.ascii_letters) for i in xrange(15))
    sock.connect((ip,port))
    response=sock.recv(1024)
    while(response.find("\n")==-1):
      response+=sock.recv(1024)
    sock.send("REG "+flag+"\n")
    response=sock.recv(1024)
    while(response.find("\r")==-1 and response.find("\n")==-1):
      response+=sock.recv(1024)
    regText=response.strip()
    self.token=regText[regText.find("+REG")+5:]
    self.flag_id=self.token[0:16];self.error=0;self.error_msg=""

    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((ip,port))
    response=sock.recv(1024)
    while(response.find("\n")==-1):
      response+=sock.recv(1024)
    sock.send("AUTH "+self.token+"\n")
    response=sock.recv(1024)
    while(response.find("\r")==-1 and response.find("\n")==-1):
      response+=sock.recv(1024)
    authText=response.strip()
    self.flag=authText[authText.find("+AUTH")+6:][:16]
    
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
