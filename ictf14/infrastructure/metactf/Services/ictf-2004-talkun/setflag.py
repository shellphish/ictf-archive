import sys,random,string
sys.path.insert(0,'.')
from utility import pybrowse,browserpersonality
class SetFlag():
  def execute(self,ip,port,flag):
    self.flag_id="".join(random.choice(string.letters) for i in xrange(8))
    self.token="".join(random.choice(string.letters) for i in xrange(8))
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
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
