import random,socket,string,time,os
random.seed(os.urandom(20))
class SetFlag():
  def execute(self,ip,port,flag):
    self.token="".join(random.choice(string.letters)for i in xrange(random.randint(8,8)))
    self.flag_id="".join(random.choice(string.letters)for i in xrange(random.randint(6,8)))
    fullname = self.flag_id + self.token
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    candidate = str(random.randint(1,5))
    s.connect((ip,port))
    s.send("POST /cgi-bin/feedback.php HTTP/1.1\nHost:"+ip+"\nContent-Type:application/x-www-form-urlencoded\nContent-Length:"+str(42+len(fullname))+"\n\nname="+fullname+"&comment="+flag+"&candidate="+candidate)
    #received = s.recv(1024)
    time.sleep(3)
    s.close()
    print "Flag ID is ", self.flag_id
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
