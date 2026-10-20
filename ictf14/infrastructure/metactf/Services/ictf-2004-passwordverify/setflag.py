import random,socket,string
class SetFlag():
  def execute(self,ip,port,flag):
    self.flag_id="".join(random.choice(string.letters)for i in xrange(random.randint(6,8)))
    self.token="".join(random.choice(string.letters)for i in xrange(random.randint(6,8)))
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((ip,port))
#    print "connceted, ", self.flag_id, ",", self.token, ", ", flag
    data_sent = s.send("STORE "+self.flag_id+"-"+self.token+" "+flag+"\n")
#    print "send", data_sent
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
