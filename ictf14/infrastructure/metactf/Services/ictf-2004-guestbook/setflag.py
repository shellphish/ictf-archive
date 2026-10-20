import random,sys
sys.path.insert(0,'.')
from utility import CtfUtil,pybrowse
class SetFlag():
  def execute(self,ip,port,flag):
    first=CtfUtil.getRandomString(random.randint(6,8))
    last=CtfUtil.getRandomString(random.randint(6,8))
    mainpage=pybrowse.Browser("http://"+ip+":"+str(port)+"/guestbook/feedback.html")
    mainpage.open()
    mainpage.parse()
    print mainpage
    mainpage.forms[0].fields['first']=first
    mainpage.forms[0].fields['last']=last
    mainpage.forms[0].fields['private']="yes"
    mainpage.forms[0].fields['comment']=flag
    print flag
    mainpage.forms[0].click(None)
    self.token=last
    self.flag_id=first;self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
