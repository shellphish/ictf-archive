import sys
sys.path.insert(0,'.')
from utility import CtfUtil,pybrowse,browserpersonality
class SetFlag():
  def execute(self,ip,port,flag):
    randomName=CtfUtil.getRandomString(10)
    mainpg=pybrowse.Browser("http://"+ip+"/ictf-2005-spamgen/cgi-bin/spamgen.py?action=upload",browserpersonality.getRandomPersonality(),debug=0)
    #mainpg=pybrowse.Browser("http://"+ip+"/~spamgen/cgi-bin/spamgen.py?action=upload",browserpersonality.getRandomPersonality(),debug=0)
    mainpg.open()
    mainpg.parse()
    mainpg.forms[0].fields["uname"]=randomName
    mainpg.forms[0].fields["pwd"]="miconsenta"
    mainpg.forms[0].fields["thetext"]=flag
    mainpg.forms[0].click(None)
    self.token=randomName+':'+"miconsenta"
    self.flag_id="";self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
