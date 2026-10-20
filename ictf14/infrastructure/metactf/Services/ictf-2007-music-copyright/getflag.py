import sys
sys.path.insert(0,'.')
from utility import pybrowse
class GetFlag():
  def execute(self,ip,port,flag_id,token):
    mainpg=pybrowse.Browser("http://"+ip+":" + str(port) + "/Sound_of_music_files/widget2_markup.html")
    mainpg.open()
    mainpg.parse()
    mainpg.forms[0].fields["email"]=flag_id
    mainpg.forms[0].fields["password"]=token
    resultingPage=mainpg.forms[0].click(None)
    resultingPage=pybrowse.Browser("http://"+ip+":" + str(port) + "/cgi-bin/star.php",resultingPage.personality,resultingPage.referer,resultingPage.cookies)
    resultingPage.open()
    self.flag=resultingPage.page[resultingPage.page.find("Hello ")+6:].split(",<")[0]
    self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}

