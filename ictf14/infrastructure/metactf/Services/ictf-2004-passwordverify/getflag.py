import socket, time
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    time.sleep(1)
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((ip,port))
    s.send("DICT "+flag_id+"-"+token+"\n")
    self.flag=s.recv(16)
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
