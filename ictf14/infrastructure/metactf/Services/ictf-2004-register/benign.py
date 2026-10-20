import sys
import random
from utility import CtfUtil,pybrowse,browserpersonality
sys.path.insert(0,'.')
class Benign():

    def do_benign(self, s, username, password):
        pass
        
    def execute(self, ip, port, flag_id, token):
        mainpg=pybrowse.Browser("http://"+ip+ ':' + str(port),browserpersonality.getRandomPersonality())
        #mainpg=pybrowse.Browser("http://"+ip+"/~register/register.html",browserpersonality.getRandomPersonality())
        mainpg.open()
        mainpg.parse()
        wwid=CtfUtil.getRandomAlphaNum(8)
        passwd = CtfUtil.getRandomAlphaNum(12)
        mainpg.forms[0].fields['first']=CtfUtil.getRandomString(random.randint(5,7))
        mainpg.forms[0].fields['last']=CtfUtil.getRandomString(random.randint(6,9))
        mainpg.forms[0].fields['dob']=str(random.choice(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']))+" "+str(random.randint(1,29))+", "+str(random.randint(1900,2000))
        mainpg.forms[0].fields['email']=CtfUtil.getRandomEmail()
        mainpg.forms[0].fields['password']=passwd
        mainpg.forms[0].fields['wwid']=wwid
        mainpg.forms[0].click(None)        
        mainpg=pybrowse.Browser("http://"+ip+':'+str(port) ,browserpersonality.getRandomPersonality())
        mainpg.open()
        mainpg.parse()
        mainpg.forms[1].fields["password"]=passwd
        mainpg.forms[1].fields["wwid"]=wwid
        resultingPage=mainpg.forms[1].click(None)
        target_wwid = resultingPage.page.split('name=\"wwid\" value=\"')[1].split('\"')[0]
        self.flag_id = ''
        self.error = -1
        self.error_msg = 'wwid not matching'
        self.token = ''
        if target_wwid == wwid:
            self.flag_id = flag_id        
            self.token = token
            self.error=0;self.error_msg=""
        
    def result(self):
        if self.error == 0:
            return {'FLAG_ID' : self.flag_id,
                'TOKEN' : self.token,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }
        else:
            return {
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }
