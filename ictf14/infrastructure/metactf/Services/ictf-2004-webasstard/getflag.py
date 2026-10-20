import urllib,socket
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.connect((ip,2345))
    sock.send(token)
    response=sock.recv(1024)
    while(response.find("+")==-1):
      response+=sock.recv(1024)
    self.flag=urllib.unquote_plus(response[response.find("+")+1:])
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
