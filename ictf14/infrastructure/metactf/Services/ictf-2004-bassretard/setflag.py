import sys,random
sys.path.insert(0,'.')
from utility import CtfUtil,pybrowse,browserpersonality

class SetFlag():
  def execute(self,ip,port,flag):
    mainpg=pybrowse.Browser("http://"+ip+":10080/",browserpersonality.getRandomPersonality())
    mainpg.open()
    mainpg.parse()
    flag_id=CtfUtil.getRandomString(random.randint(7,9))
    mainpg.forms[0].fields['user']=flag_id
    mainpg.forms[0].fields['email']=CtfUtil.getRandomEmail()
    mainpg.forms[0].fields['note']=flag
    mainpg.forms[0].click(None)
    self.token=mainpg.forms[0].fields['user']+":"+mainpg.forms[0].fields['email']
    self.error=0;self.error_msg=""
    self.flag_id = flag_id

  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
#s = SetFlag()
#s.execute("192.168.56.102", 10082, "FLGOjgIf1MtHjhgK")
#print s.result()
