import random,sys
sys.path.insert(0,'.')
from utility import CtfUtil,pybrowse
class SetFlag():
  def execute(self,ip,port,flag):
    db_admin = "admin"
    db_admin_password = "fuckyou123"
    first=CtfUtil.getRandomString(5)
    last=CtfUtil.getRandomString(random.randint(6,8))
    contactChangePage=pybrowse.Browser("http://"+ip+":" + str(port) + "/cgi-bin/contact_change.pl?login="+db_admin+"&password="+db_admin_password+"&first="+first+"&last="+last+"&ext="+flag)
    contactChangePage.open()
    if not "Update Successful" in contactChangePage.page:
       self.error = 1
       self.error_msg = "Admin authentication failure"
    self.token=last
    self.flag_id=first
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
