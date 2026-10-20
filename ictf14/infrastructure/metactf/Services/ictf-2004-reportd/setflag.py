import socket,random,sys
sys.path.insert(0,'.')
from utility import CtfUtil
class SetFlag():
  def execute(self,ip,port,flag):
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((ip,port))
    response=sock.recv(1024)
    sock.send("1\n")
    sock.send(str(random.randint(1,8))+"\n")
    sock.send(CtfUtil.getRandomString(random.randint(6,8))+"\n")
    sock.send(str(random.randint(1,100))+"\n")
    flag_id = CtfUtil.getRandomString(6)
    sock.send(flag_id + ':' +flag+"\n")    
    while(response.find("continue")==-1):
      response+=sock.recv(1024)
    sock.close()
    #print 'SetFlag:' + response
    self.token=response[response.find("Bas-ID is:")+11:].split("\n")[0]
    self.flag_id=flag_id;self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
