import httplib
import urllib
import re
import random

from ImageScripts.BaseScoringScript import BaseScoringScript 
from ImageScripts.Utility import pybrowse, browserpersonality

hex = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A','B','C','D','E','F']

class AcquireScoringScript(BaseScoringScript):
    
    def doScoring(self):
        """
        this is the entry point for the scoring script.
        """
        
        personality = browserpersonality.getRandomPersonality()
        
        if self.cookie != None:
            try:
                getFlagUrl = self.teamIp+"/~acquire/cgi-bin/get.php?ip="+self.cookie
                getFlagPage = pybrowse.Browser("http://" + getFlagUrl)
                getFlagPage.open()
            
                rawPage = getFlagPage.page
            
                successPattern = "entry was "
                successPtr = rawPage.find(successPattern)

                if successPtr < 0:
                    print "Failed to retrieve a flag!"
                    self.returnVal.setError()
                    return

                oldFlag = rawPage[successPtr+48:][:self.getFlagSize()]
                self.validatePreviousFlag(oldFlag)
                
            except Exception, e:
                self.output.write("got exception '%s' when getting flag" % (e))
                self.returnVal.setConnectFailed()
                return
            
        #set new flag
        try:
            ipv6 = ""
        
            for i in range(32):
                ipv6 += random.choice(hex)
            
            setFlagUrl = self.teamIp+"/~acquire/cgi-bin/set.php?ip="+ipv6+"&net=ucsb&de="+urllib.quote(self.getNewFlagText())
        
            mainpg = pybrowse.Browser("http://" + setFlagUrl)
            mainpg.open()
            resultPage = mainpg.page
            
            successPattern = "new spam relay"
            successPtr = resultPage.find(successPattern)

            if successPtr < 0:
                print "Failed to post new flag!"
                self.returnVal.setPostFlagFailed()
                return
            
            self.cookie = ipv6
            self.returnVal.setSuccess()
            
        except Exception, e:
            self.output.write("got exception '%s' when setting flag" % (e))
            self.returnVal.setError()
            return
    
    def exerciseService(self):
         if self.cookie != None:
            try:
                getFlagUrl = self.teamIp+"/~acquire/cgi-bin/get.php?ip="+self.cookie
                getFlagPage = pybrowse.Browser("http://" + getFlagUrl)
                getFlagPage.open()
            except:
                pass
    
def getScoringScript():
    """
    this must be defined in every scoring module.
    """
    return AcquireScoringScript