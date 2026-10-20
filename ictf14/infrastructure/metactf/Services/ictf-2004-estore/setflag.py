import random,sys
sys.path.insert(0,'.')
from utility import CtfUtil,pybrowse
class SetFlag():
  def execute(self,ip,port,flag):

    userurl = "http://"+ip+":" + str(port) + "/cgi-bin/createuser.php"
    print "Connecting to ", userurl
    userPage = pybrowse.Browser(userurl)
    #userPage=pybrowse.Browser("http://"+ip+"/~estore/cgi-bin/createuser.php")
    userPage.open()
    userPage.parse()
    userName=CtfUtil.getRandomString(random.randint(6,8))
    password=CtfUtil.getRandomAlphaNum(8)
    userPage.forms[0].fields['username']=userName
    userPage.forms[0].fields['password']=password
    userPage.forms[0].fields['email']=flag
    userPage.forms[0].click(None)
    self.token=password
    self.flag_id=userName;self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
