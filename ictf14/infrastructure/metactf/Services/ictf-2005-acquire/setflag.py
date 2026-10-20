import random,sys,urllib
sys.path.insert(0,'.')
from utility import pybrowse
class SetFlag():
  def execute(self,ip,port,flag):
    random.seed()
    ipv6=""
    for i in range(32):
      ipv6+=random.choice(['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'])
    mainpg=pybrowse.Browser("http://"+ip+":"+str(port)+"/acquire/cgi-bin/set.php?ip="+ipv6+"&net=ucsb&de="+urllib.quote(flag))
    mainpg.open()
    self.flag_id=ipv6[:16]
    self.token=ipv6[16:32]
    self.error=0
    self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
