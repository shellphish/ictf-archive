import sys,random
sys.path.insert(0,'.')
from utility import pybrowse,CtfUtil
class SetFlag():
  def execute(self,ip,port,flag):
    self.flag_id = CtfUtil.getRandomEmail()
    mainpg=pybrowse.Browser("http://"+ip+":" + str(port) + "/Petition_files/widget1_markup.html")
    #mainpg=pybrowse.Browser("http://"+ip+"/Site//Petition_files/widget1_markup.html")
    mainpg.open()
    mainpg.parse()
    mainpg.forms[0].fields["first"]=CtfUtil.getRandomString(random.randint(4,10))
    mainpg.forms[0].fields["last"]=CtfUtil.getRandomString(random.randint(4,10))
    mainpg.forms[0].fields["email"]=self.flag_id
    mainpg.forms[0].fields["comment"]=flag
    mainpg.forms[0].fields["id"]=""
    resultingPage=mainpg.forms[0].click(None)
    self.token=resultingPage.page[resultingPage.page.find("Your ID is ")+11:][:8]
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
