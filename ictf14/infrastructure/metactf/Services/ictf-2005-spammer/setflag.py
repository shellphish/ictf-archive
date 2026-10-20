import sys,random,socket
sys.path.insert(0,'.')
from utility import CtfUtil

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
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((ip,port))
    username=CtfUtil.getRandomString(6)
    password=random.choice(['bbbccc','aaabbb','cccddd'])
    s.send('new %s %s\n'%(username,password))
    s.send("to: xxxx\n")
    s.send("spam\n")
    s.send("%s\n"%flag)
    s.send(".\n")
    s.send("exit\n")
    received = rtil_str(s,"Bey Bey")
    s.close()
    self.token=password
    self.flag_id=username;self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
