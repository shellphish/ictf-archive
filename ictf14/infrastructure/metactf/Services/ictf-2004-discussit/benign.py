import socket
import sys
from utility import CtfUtil
sys.path.insert(0,'.')

class Benign():
    
    def execute(self, ip, port, flag_id, token):
        uname = CtfUtil.getRandomString(4)
        topic = CtfUtil.getRandomString(4)
        got_shell = False
        re_tries = 5
        sock = None
        self.flag = ''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
                    
        # Preamble
        sock.send(uname + " "+topic+"\n")
        #sock.sendall("test test\n")
        sock.recv(38)
        sock.recv(139)
        #time.sleep(0.2)
        sock.sendall(CtfUtil.getRandomString(12))
        sock.close()
        self.flag_id = flag_id
        self.token = token
        self.error = 0
        self.error_msg = ""
    
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
