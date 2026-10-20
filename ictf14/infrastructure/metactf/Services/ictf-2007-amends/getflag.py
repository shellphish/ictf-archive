import sys
sys.path.insert(0,'.')
from utility import pybrowse,browserpersonality
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    mainpg=pybrowse.Browser("http://"+ip+":" + str(port) + "/cgi-bin/settlement.php",browserpersonality.getRandomPersonality())
    #mainpg=pybrowse.Browser("http://"+ip+"/~amends/cgi-bin/settlement.php",browserpersonality.getRandomPersonality())
    mainpg.open()
    mainpg.parse()
    mainpg.forms[0].fields['email']=flag_id
    mainpg.forms[0].fields['caseid']=token
    resultPage=mainpg.forms[0].click(None)
    resultPage=resultPage.doRedirects()
    self.flag=resultPage.page[resultPage.page.find("card number:")+21:][:16]
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
