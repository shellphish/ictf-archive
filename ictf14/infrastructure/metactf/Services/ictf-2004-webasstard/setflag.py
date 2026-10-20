import random,sys
sys.path.insert(0,'.')
from utility import CtfUtil,pybrowse


class SetFlag():
  def execute(self,ip,port,flag):
    mainpage=pybrowse.Browser("https://"+ip+":"+str(port))
    mainpage.open()
    mainpage.parse()
    user=CtfUtil.getRandomString(random.randint(16,20))
    mainpage.forms[0].fields['user']=user
    mainpage.forms[0].fields['password']="miconsenta"
    mainpage.forms[0].fields['operation']="OP-store"
    storeFilePage=mainpage.forms[0].click(None)
    storeFilePage.parse()
    storeFilePage.forms[0].fields['filename']=user
    storeFilePage.forms[0].fields['content']=flag
    storeFilePage.forms[0].click(None)
    
    self.token=user
    self.flag_id=self.token[:8]
    self.error=0
    self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
         