import sys
sys.path.insert(0,'.')
from utility import pybrowse,browserpersonality
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    resultPage=pybrowse.Browser("http://"+ip+":"+str(port)+"/notes?username="+flag_id+token,browserpersonality.getRandomPersonality())
    resultPage.open()
    self.flag=resultPage.page[resultPage.page.find("["+flag_id+token+":")+len(flag_id+token)+2:][:16]
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
