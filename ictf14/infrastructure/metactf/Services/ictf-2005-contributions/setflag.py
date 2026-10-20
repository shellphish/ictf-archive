import random,sys
import urllib
import os
random.seed(os.urandom(20))
sys.path.insert(0,'.')
from utility import CtfUtil,pybrowse
class SetFlag():
  def execute(self,ip,port,flag):
    name=CtfUtil.getRandomString(random.randint(8,12))
    flag_id = str(random.randint(1,999999999))
    mainpg=pybrowse.Browser("http://"+ip+":" + str(port) + "/contribute.html")
    #mainpg=pybrowse.Browser("http://"+ip+"/~contribute/contribute.html")
    mainpg.open()
    mainpg.parse()
    mainpg.forms[0].fields['name']=name
    mainpg.forms[0].fields['address']=flag
    mainpg.forms[0].fields['ccn']=str(random.randint(1,999999999999))
    mainpg.forms[0].fields['contribution']=flag_id
    mainpg = mainpg.forms[0].click(None)
    mainpg.parse()
    self.token=name
    self.flag_id=flag_id;self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
