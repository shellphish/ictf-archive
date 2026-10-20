import sys
sys.path.insert(0,'.')
from utility import pybrowse
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    getFlagPage=pybrowse.Browser("http://"+ip+":"+str(port)+"/acquire/cgi-bin/get.php?ip="+flag_id+token)
    getFlagPage.open()
    self.flag=getFlagPage.page[getFlagPage.page.find(flag_id+token)+38:].split("\n")[0]
    self.flag = self.flag.rstrip()
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
