# Modified by EDG 2015/4/1
# Un-uglify; implement flag_id

import sys,random,urllib
sys.path.insert(0,'.')
from utility import CtfUtil,pybrowse

class SetFlag():
  def execute(self,ip,port,flag):
    first=CtfUtil.getRandomString(random.randint(6,8))
    last=CtfUtil.getRandomString(random.randint(6,8))
    mainpg=pybrowse.Browser("http://" + ip+":" + str(port) + "/cgi-bin/museum_upload.pl?first="+first+"&last="+last+"&dob=&ssn=&mmn=&email=&idea="+urllib.quote(flag))
    mainpg.open()
    self.token=last
    self.flag_id=first
    self.error=0
    self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
