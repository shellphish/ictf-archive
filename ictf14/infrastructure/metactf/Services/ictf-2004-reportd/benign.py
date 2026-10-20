import socket
import random
from utility import CtfUtil
class Benign():
    def execute(self,ip,port,flag_id,token):
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((ip,port))
        received=sock.recv(1024)
        sock.send("1\n")
        sock.send(str(random.randint(1,8))+"\n")
        sock.send(CtfUtil.getRandomString(random.randint(6,8))+"\n")
        sock.send(str(random.randint(1,100))+"\n")
        sock.send(CtfUtil.getRandomString(random.randint(1,2))+"\n")        
        response = received
        while(response.find("continue")==-1):
          response += sock.recv(1024)
        sock.close()  
        self.error=0;self.error_msg=""
        
        self.flag_id = flag_id
        self.token = token
    
    def result(self):
        if self.error == 0:
            return {'FLAG_ID' : self.flag_id,
                'TOKEN' : self.token,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }
        else:
            return {
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }
