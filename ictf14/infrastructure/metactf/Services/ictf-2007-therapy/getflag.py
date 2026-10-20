import sys
sys.path.insert(0,'.')
from utility import pybrowse
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    username,password = token.split(":")
    mainpg=pybrowse.Browser("http://"+ip+":"+str(port)+"/Therapy/login.do")
    mainpg.open()
    mainpg.parse()
    mainpg.forms[0].fields['username']=username
    mainpg.forms[0].fields['password']=password
    resultPage=mainpg.forms[0].click(None)
    resultPage.parse()
    resultPage=resultPage.click(resultPage.links[9])
    self.flag=resultPage.page[resultPage.page.find("addinfo")+21:][:16]
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
