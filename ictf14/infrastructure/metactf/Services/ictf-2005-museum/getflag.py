import sys
sys.path.insert(0,'.')
from utility import pybrowse
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    getFlagPage=pybrowse.Browser("http://"+ip+ ":" + str(port) + "/cgi-bin/museum_admin.pl?first=" + flag_id + "&last=" + token + "&password=unbreakable")
    getFlagPage.open()
    self.flag=getFlagPage.page[253:][:16]
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
