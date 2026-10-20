import sys
sys.path.insert(0,'.')
from utility import pybrowse,CtfUtil
def update(ip,port,token,flag,flag_id):
  updatePage=pybrowse.Browser("http://"+ip+":" + str(port) + "/cgi-bin/update.php")
  #updatePage=pybrowse.Browser("http://"+ip+"/~estore/cgi-bin/update.php")
  updatePage.open()
  updatePage.parse()
  updatePage.forms[0].fields['username']=flag_id
  updatePage.forms[0].fields['password']=token
  updatePage.forms[0].fields['newemail']=flag
  return updatePage.forms[0].click(None).page[updatePage.forms[0].click(None).page.find("address was:")+13:][:16]
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    flag=update(ip,port,token,"",flag_id)
    update(ip,port,token,flag,flag_id)
    self.flag=flag
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
