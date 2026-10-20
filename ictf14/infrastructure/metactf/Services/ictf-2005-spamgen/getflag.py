import sys
sys.path.insert(0,'.')
from utility import pybrowse,browserpersonality
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    mainpg=pybrowse.Browser("http://"+ip+"/ictf-2005-spamgen/cgi-bin/spamgen.py?action=read",browserpersonality.getRandomPersonality(),debug=0)
    #mainpg=pybrowse.Browser("http://"+ip+"/~spamgen/cgi-bin/spamgen.py?action=read",browserpersonality.getRandomPersonality(),debug=0)
    mainpg.open()
    mainpg.parse()
    mainpg.forms[0].fields["uname"]=token.split(':')[0]
    mainpg.forms[0].fields["pwd"]=token.split(':')[1]
    resultingPage=mainpg.forms[0].click(None)
    self.flag=resultingPage.page[resultingPage.page.find("</h3>")+6:][:16]
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
