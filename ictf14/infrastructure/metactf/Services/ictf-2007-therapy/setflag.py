import sys,random
sys.path.insert(0,'.')
from utility import CtfUtil,pybrowse
class SetFlag():
  def execute(self,ip,port,flag):
    username=CtfUtil.getRandomString(random.randint(6,10))
    password=CtfUtil.getRandomString(random.randint(4,10))
    email=CtfUtil.getRandomEmail()
    mainpg=pybrowse.Browser("http://"+ip+":"+str(port)+"/Therapy/createuser.do?role=client")
    mainpg.open()
    mainpg.parse()
    mainpg.forms[0].fields['email']=email
    mainpg.forms[0].fields['username']=username
    mainpg.forms[0].fields['password']=password
    mainpg=mainpg.forms[0].click("submit")
    mainpg=mainpg.click("clients.do?action=create")
    mainpg.parse()
    mainpg.forms[0].fields['addinfo']=flag
    mainpg=mainpg.forms[0].click("submit")
    self.token=username + ":" + password
    self.flag_id=email;
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
