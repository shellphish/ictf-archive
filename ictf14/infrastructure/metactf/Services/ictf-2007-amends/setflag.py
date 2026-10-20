import sys,random
sys.path.insert(0,'.')
from utility import CtfUtil,pybrowse,browserpersonality
class SetFlag():
  def execute(self,ip,port,flag):
    eaddr=CtfUtil.getRandomEmail()
    mainpg=pybrowse.Browser("http://"+ip+":" +str(port) + "/Make_amends_files/widget1_markup.html",browserpersonality.getRandomPersonality())
    #mainpg=pybrowse.Browser("http://"+ip+"/Site/Make_amends_files/widget1_markup.html",browserpersonality.getRandomPersonality())
    mainpg.open()
    mainpg.parse()
    mainpg.forms[0].fields['first']=CtfUtil.getRandomString(random.randint(6,10))
    mainpg.forms[0].fields['last']=CtfUtil.getRandomString(random.randint(6,10))
    mainpg.forms[0].fields['email']=eaddr
    dollars=""
    for i in range(random.randint(1,5)):
      dollars+=random.choice(['0','1','2','3','4','5','6','7','8','9'])
    cents=""
    for i in range(2):
      cents+=random.choice(['0','1','2','3','4','5','6','7','8','9'])
    mainpg.forms[0].fields['price']=dollars+'.'+cents
    mainpg=mainpg.forms[0].click(None)
    mainpg.parse()
    mainpg=mainpg.forms[0].click(None)
    caseid=mainpg.page[mainpg.page.find("CASE ID #")+19:][:16]
    otherpg=pybrowse.Browser("http://"+ip+"/ictf-2007-amends/cgi-bin/settlement.php",browserpersonality.getRandomPersonality())
    #otherpg=pybrowse.Browser("http://"+ip+"/~amends/cgi-bin/settlement.php",browserpersonality.getRandomPersonality())
    otherpg.open()
    otherpg.parse()
    otherpg.forms[0].fields['email']=eaddr
    otherpg.forms[0].fields['caseid']=caseid
    otherpg=otherpg.forms[0].click(None)
    otherpg=otherpg.doRedirects()
    otherpg.parse()
    otherpg.forms[0].fields['ccnum']=flag
    otherpg.forms[0].click(None)
    self.token=caseid
    self.flag_id=eaddr;self.error=0;self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
