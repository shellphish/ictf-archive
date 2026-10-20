import sys
sys.path.insert(0,'.')
from utility import pybrowse
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    mainpg=pybrowse.Browser("http://"+ip+":" + str(port) + "/petition/Petition_files/widget1_markup.html")
    #mainpg=pybrowse.Browser("http://"+ip+"/Site//Petition_files/widget1_markup.html")
    mainpg.open()
    mainpg.parse()
    mainpg.forms[0].fields["id"]=token
    self.flag=mainpg.forms[0].click(None).page[mainpg.forms[0].click(None).page.find("Your comment was:")+18:][:16]
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
