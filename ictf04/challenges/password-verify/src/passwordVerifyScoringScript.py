import socket
import random

from ImageScripts.BaseScoringScript import BaseScoringScript 
from ImageScripts.Utility import pybrowse, browserpersonality

class PasswordVerifyScoringScript(BaseScoringScript):

    def sendMessage(self, message):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.teamIp, 11111))
        s.send(message)
            
        response = s.recv(1024)
        s.close()
        
        return response
    
    def doScoring(self):
        #get old flag
        if self.cookie != None:
            try:
                name = self.cookie
                msg = "DICT " + name + "\n"
                response = self.sendMessage(msg)
                self.validatePreviousFlag(response)
            except Exception, e:
                self.output.write("got exception %s getting flag" % (e))
                self.returnVal.setError()
       
        #set the new flag
        try:  
            name = self.getRandomString(random.randint(6,8))
            msg = "STORE "+name+" " + self.getNewFlagText() + "\n"    
            response = self.sendMessage(msg)
            
            successPtr = response.find("included in")
            if successPtr == -1:
                self.returnVal.setPostFlagFailed()
                return
            
            self.cookie = name
            self.returnVal.setSuccess()
           
        except Exception, e:
            self.returnVal.setError()
            self.output.write("got exception %s setting new flag" % (e))
            
    def exerciseService(self):
        if(self.cookie):
            name = self.cookie
            msg = "CHECK " + name + " " + self.getRandomString(5) + "\n"

        
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return PasswordVerifyScoringScript