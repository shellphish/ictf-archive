import random,string,socket
class SetFlag():
  def execute(self,ip,port,flag):
    name="".join(random.choice(string.letters)for i in xrange(random.randint(6,8)))
    id="".join(random.choice(string.letters+string.digits)for i in xrange(6))
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((ip,port))
    options={
      0:"schmidt=-1%20" + flag + "&blitzkrieg=" + str(random.randint(1,100)) + \
      "&stallone=" + str(random.randint(1,100)) + \
      "&blix="+str(random.randint(1,100)) + \
      "&schtrappe=" + str(random.randint(1,100)),\
      1:"schmidt=" + str(random.randint(1,100)) + \
      "&blitzkrieg=-1%20" + flag + \
      "&stallone=" + str(random.randint(1,100)) + \
      "&blix=" + str(random.randint(1,100)) + \
      "&schtrappe=" + str(random.randint(1,100)),\
      2:"schmidt="+str(random.randint(1,100))+"&blitzkrieg="+str(random.randint(1,100))+"&stallone=-1%20"+flag+"&blix="+str(random.randint(1,100))+"&schtrappe="+str(random.randint(1,100)),
      3:"schmidt="+str(random.randint(1,100))+"&blitzkrieg="+str(random.randint(1,100))+"&stallone="+str(random.randint(1,100))+"&blix=-1%20"+flag+"&schtrappe="+str(random.randint(1,100)),
      4:"schmidt="+str(random.randint(1,100))+"&blitzkrieg="+str(random.randint(1,100))+"&stallone="+str(random.randint(1,100))+"&blix="+str(random.randint(1,100))+"&schtrappe=-1%20"+flag
    }
    s.send("GET /ictf-2004-pollit/cgi-bin/poll.pl?username="+name+"&pollid="+id+"&"+options[random.randint(0,4)]+"&scope=local&op=upload\n")
    self.token=name+":"+id
    self.flag_id="puppa";self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
