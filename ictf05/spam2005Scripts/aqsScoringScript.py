import httplib
import urllib
import random
import re

from ImageScripts.BaseScoringScript import BaseScoringScript 
from ImageScripts.Utility import pybrowse, browserpersonality

class AqsScoringScript(BaseScoringScript):
    
    def doScoring(self): 
        personality = browserpersonality.getRandomPersonality()
        
        if self.cookie != None:
            try:
                getFlagUrl = self.teamIp+"/~aqs/cgi-bin/guestbook.py?name="+self.cookie+"&command=lookup"
                getFlagPage = pybrowse.Browser("http://" + getFlagUrl)
                getFlagPage.open()
            
                rawPage = getFlagPage.page
                
                successPattern = self.cookie
                successPtr = rawPage.find(successPattern)

                if successPtr < 0:
                    self.returnVal.setError()
                    return
                
                successPtr += len(self.cookie)
                oldFlag = rawPage[successPtr+8:][:self.getFlagSize()]
                self.validatePreviousFlag(oldFlag)
                
            except Exception, e:
                self.output.write("got exception '%s' when getting flag" % (e))
                self.returnVal.setConnectFailed()
                return
        
        #set new flag
        try:
            randomName = self.getRandomString(random.randint(6,8))
            
            setFlagUrl = self.teamIp+"/~aqs/cgi-bin/guestbook.py?name="+randomName+"&comment="+self.getNewFlagText()+"&priv=on&command=sign"
        
            mainpg = pybrowse.Browser("http://" + setFlagUrl)
            mainpg.open()
            resultPage = mainpg.page
            
            successPattern = "Thanks for signing"
            successPtr = resultPage.find(successPattern)

            if successPtr < 0:
                self.returnVal.setPostFlagFailed()
                return
            
            self.cookie = randomName
            self.returnVal.setSuccess()
            
        except Exception, e:
            self.output.write("got exception '%s' when setting flag" % (e))
            self.returnVal.setError()
            return
    
    def exerciseService(self):
         if self.cookie != None:
            try:
                getFlagUrl = self.teamIp+"/~aqs/cgi-bin/guestbook.py?name="+self.cookie+"&command=lookup"
                getFlagPage = pybrowse.Browser("http://" + getFlagUrl)
                getFlagPage.open()
            except:
                pass
    
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return AqsScoringScript