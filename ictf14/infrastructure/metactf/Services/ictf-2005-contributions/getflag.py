import sys
import urllib
sys.path.insert(0,'.')
from utility import pybrowse
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    getFlagPage=pybrowse.Browser("http://"+ip+":" + str(port) + "/cgi-bin/history.py?name="+token)
    #getFlagPage=pybrowse.Browser("http://"+ip+"/~contribute/cgi-bin/history.py?name="+token)
    getFlagPage.open()
    self.flag=getFlagPage.page[getFlagPage.page.find("address")+8:][:16]
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
