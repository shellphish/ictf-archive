import sys
sys.path.insert(0,'.')
from utility import pybrowse
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    guestPage=pybrowse.Browser("http://"+ip+":"+str(port)+"/guestbook/cgi-bin/guestbook.pl?user="+flag_id+"&pass="+token)
    guestPage.open()
    self.flag=guestPage.page[guestPage.page.find(flag_id+" "+token)+len(flag_id)+len(token)+30:][:16]
    self.flag = self.flag.split("<")[0]
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
