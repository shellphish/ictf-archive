import socket,time
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    time.sleep(.01)
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((ip,port))
    s.send("GET /ictf-2004-pollit/cgi-bin/poll.pl?username="+token.split(":")[0]+"&pollid="+token.split(":")[1]+"&scope=local&op=review\n")
    self.flag="FLG"+s.recv(516).split("FLG")[1][:13]
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
