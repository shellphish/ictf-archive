import sys
sys.path.insert(0,'.')
from utility import pybrowse,browserpersonality
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    mainpg=pybrowse.Browser("http://"+ip+':'+str(port) ,browserpersonality.getRandomPersonality())
    #mainpg=pybrowse.Browser("http://"+ip+"/~register/register.html",browserpersonality.getRandomPersonality())
    mainpg.open()
    mainpg.parse()
    mainpg.forms[1].fields["password"]=token
    mainpg.forms[1].fields["wwid"]=flag_id
    resultingPage=mainpg.forms[1].click(None)
    target_wwid = resultingPage.page.split('name=\"wwid\" value=\"')[1].split('\"')[0]
    self.flag = ''
    self.error = -1
    self.error_msg = 'wwid not matching'
    if target_wwid == flag_id:
        self.flag = token        
        self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
