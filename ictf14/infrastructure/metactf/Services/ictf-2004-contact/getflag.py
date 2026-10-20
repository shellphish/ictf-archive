import sys,socket
sys.path.insert(0,'.')
from utility import pybrowse
class GetFlag():
  def execute(self,ip,port,flag_id,token):

    contactPage=pybrowse.Browser("http://"+ip+":" + str(port) + "/contact.html")
    contactPage.open()
    contactPage.parse()
    contactPage.forms[0].fields['cboname']=token

    info = contactPage.forms[0].click(None).page[contactPage.forms[0].click(None).page.find(flag_id)+14:]
    self.flag=info.split("<")[0] 
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
