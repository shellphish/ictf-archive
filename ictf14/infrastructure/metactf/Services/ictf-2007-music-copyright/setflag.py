import sys,random
sys.path.insert(0,'.')
from utility import pybrowse,CtfUtil
class SetFlag():
  def execute(self,ip,port,flag):
    mainpg=pybrowse.Browser("http://"+ip+":" + str(port) + "/Sound_of_music_files/widget1_markup.html")
    mainpg.open()
    mainpg.parse()
    mainpg.forms[0].fields["first"]=flag
    mainpg.forms[0].fields["last"]=CtfUtil.getRandomString(random.randint(3,10))
    self.flag_id=CtfUtil.getRandomEmail()
    mainpg.forms[0].fields["email"]=self.flag_id
    self.token=CtfUtil.getRandomString(random.randint(8,10))
    mainpg.forms[0].fields["password"]=self.token
    resultingPage=mainpg.forms[0].click(None)
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
