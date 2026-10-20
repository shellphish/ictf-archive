import sys,random
sys.path.insert(0,'.')
from utility import CtfUtil,pybrowse,browserpersonality
class SetFlag():
  def execute(self,ip,port,flag):
    mainpg=pybrowse.Browser("http://"+ip+ ':' + str(port),browserpersonality.getRandomPersonality())
    #mainpg=pybrowse.Browser("http://"+ip+"/~register/register.html",browserpersonality.getRandomPersonality())
    mainpg.open()
    mainpg.parse()
    wwid=CtfUtil.getRandomAlphaNum(8)
    mainpg.forms[0].fields['first']=CtfUtil.getRandomString(random.randint(5,7))
    mainpg.forms[0].fields['last']=CtfUtil.getRandomString(random.randint(6,9))
    mainpg.forms[0].fields['dob']=str(random.choice(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']))+" "+str(random.randint(1,29))+", "+str(random.randint(1900,2000))
    mainpg.forms[0].fields['email']=CtfUtil.getRandomEmail()
    mainpg.forms[0].fields['password']=flag
    mainpg.forms[0].fields['wwid']=wwid
    mainpg.forms[0].click(None)
    self.token=flag;
    self.flag_id=wwid;self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
