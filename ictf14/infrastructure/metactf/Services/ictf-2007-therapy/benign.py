import socket
import random
import sys
sys.path.insert(0,'.')
from utility import pybrowse,CtfUtil
class Benign():

        
    def execute(self, ip, port, flag_id, token):
        page1=pybrowse.Browser("http://" + ip + ":" + str(port) + "/Therapy/")
        page1.open()
        page2=pybrowse.Browser("http://" + ip + ":" + str(port) + "/Therapy/login.do")
        page2.open()
	username=CtfUtil.getRandomString(random.randint(6,10))
        password=CtfUtil.getRandomString(random.randint(4,10))
        total_bullshit=CtfUtil.getRandomString(random.randint(20,40))
        mainpg=pybrowse.Browser("http://"+ip+":"+str(port)+"/Therapy/createuser.do?role=client")
        mainpg.open()
        mainpg.parse()
        mainpg.forms[0].fields['email']=CtfUtil.getRandomEmail()
        mainpg.forms[0].fields['username']=username
        mainpg.forms[0].fields['password']=password
        mainpg=mainpg.forms[0].click("submit")
        mainpg=mainpg.click("clients.do?action=create")
        mainpg.parse()
        mainpg.forms[0].fields['addinfo']=total_bullshit
        mainpg=mainpg.forms[0].click("submit")
        self.token=password
        self.flag_id=username;
        self.error=0;self.error_msg=""        
        self.error = 0
        self.error_msg = ''
        self.flag_id = ""
        self.token = ""
        return
        
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
