import random,socket,string,re,os
random.seed(os.urandom(20))

class GetFlag():
  def execute(self,ip,port,flag_id,token):
    self.flag = ""
    candidate = str(random.randint(1,5))    
    comment="".join(random.choice(string.letters)for i in xrange(5))+" "+"".join(random.choice(string.letters)for i in xrange(random.randint(4,9)))+random.choice(['?','.','!'])
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((ip,port))
    fullname = "".join([flag_id,token])
    s.send("POST /cgi-bin/feedback.php HTTP/1.1\nHost:"+ip+"\nContent-Type:application/x-www-form-urlencoded\nContent-Length:"+str(26+len(fullname)+len(comment))+"\n\nname="+fullname+"&comment="+comment+"&candidate="+candidate)
    data = ""
    while not "</html>" in data:
        data += s.recv(1024)
        #print data
    flag_re = re.compile(r'<p>.*About \d+: (FLG\w+)</p>')
    #print data
    for line in data.splitlines():
        if "FLG" in line:
           m = flag_re.match(line)
           if m:
               self.flag = m.group(1)
    #self.flag=s.recv(924).split("About ")[1].split(": ")[1][:16]
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
