import urllib,sys,random
sys.path.insert(0,'.')
from utility import pybrowse,browserpersonality,CtfUtil
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    mainpg=pybrowse.Browser("http://"+ip+":10080/",browserpersonality.getRandomPersonality())
    mainpg.open()
    mainpg.parse()
    mainpg.forms[0].fields['user']=token.split(":")[0]
    mainpg.forms[0].fields['email']=token.split(":")[1]
    mainpg.forms[0].fields['note']=''
    resultPage=mainpg.forms[0].click(None)
    self.flag=urllib.unquote(resultPage.page[resultPage.page.find("NOTE:")+6:][:resultPage.page[resultPage.page.find("NOTE:")+6:].find("\n")])
    self.error=0;self.error_msg=""

  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}

#s = GetFlag()
#s.execute("192.168.56.102", 10082, "aaaaa", "odAfHnENF:WNZajL@nPgJUlk.org")
#print s.result()
