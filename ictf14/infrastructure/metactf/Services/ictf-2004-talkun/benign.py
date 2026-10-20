import sys,random,string
sys.path.insert(0,'.')
from utility import CtfUtil,pybrowse,browserpersonality
class Benign():
  def execute(self,ip,port,flag_id,token):
    flag=''.join(random.choice(string.ascii_letters) for i in xrange(16))
    self.flag_id="".join(random.choice(string.letters) for i in xrange(random.randint(3,4)))
    self.token="".join(random.choice(string.letters) for i in xrange(random.randint(3,4)))
    login=pybrowse.Browser("http://"+ip+":"+str(port)+"/login",browserpersonality.getRandomPersonality())
    login.open()
    login.parse()
    login.forms[0].fields['username']=self.flag_id+self.token
    login.forms[0].fields['password']="".join(random.choice(string.letters+string.digits) for i in xrange(6))
    resultPage=login.forms[0].click(None)
    resultPage.parse()
    notes=resultPage.click(resultPage.links[0])
    notes.parse()
    notes.forms[0].fields['note']=flag
    notes.forms[0].fields['line']=str(random.randint(1,100))
    notes.forms[0].fields['character']=str(random.randint(1,20))
    notes.forms[0].click(None)
    resultPage=pybrowse.Browser("http://"+ip+":"+str(port)+"/notes?username="+flag_id+token,browserpersonality.getRandomPersonality())
    resultPage.open()
    self.flag=resultPage.page[resultPage.page.find("["+flag_id+token+":")+len(flag_id+token)+2:][:16]
    self.error=0;self.error_msg=""
  def result(self):
    return {'ERROR':self.error,'ERROR_MSG':self.error_msg}
