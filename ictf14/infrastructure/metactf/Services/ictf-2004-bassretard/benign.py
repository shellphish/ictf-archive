import sys,random
import urllib
sys.path.insert(0,'.')
from utility import CtfUtil,pybrowse,browserpersonality
from utility import pybrowse,browserpersonality,CtfUtil

class Benign():
  def execute(self, ip, port, flag_id, token):
    # set flag
    flag=CtfUtil.getRandomString(random.randint(20,32))
    flag_id=CtfUtil.getRandomString(random.randint(11,13))
    mainpg=pybrowse.Browser("http://"+ip+":10080/",browserpersonality.getRandomPersonality())
    mainpg.open()
    mainpg.parse()
    mainpg.forms[0].fields['user']=flag_id
    mainpg.forms[0].fields['email']=CtfUtil.getRandomEmail()
    mainpg.forms[0].fields['note']=flag
    mainpg.forms[0].click(None)
    self.token=mainpg.forms[0].fields['user']+":"+mainpg.forms[0].fields['email']
    self.error=0;self.error_msg=""
    self.flag_id = flag_id
    
    # get the flag back
    token = self.token
    mainpg=pybrowse.Browser("http://"+ip+":10080/",browserpersonality.getRandomPersonality())
    mainpg.open()
    mainpg.parse()
    mainpg.forms[0].fields['user']=token.split(":")[0]
    mainpg.forms[0].fields['email']=token.split(":")[1]
    mainpg.forms[0].fields['note']=CtfUtil.getRandomString(random.randint(5,10))
    resultPage=mainpg.forms[0].click(None)
    self.flag=urllib.unquote(resultPage.page[resultPage.page.find("NOTE:")+6:][:resultPage.page[resultPage.page.find("NOTE:")+6:].find("\n")])[:16]
    self.error=0;self.error_msg=""

  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
