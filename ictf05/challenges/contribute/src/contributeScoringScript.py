import httplib
import urllib
import random
import re

from ImageScripts.BaseScoringScript import BaseScoringScript 
from ImageScripts.Utility import pybrowse, browserpersonality

class ContributeScoringScript(BaseScoringScript):
    
    def doScoring(self): 
        """
        this is the entry point for the scoring script.
        """
        
        personality = browserpersonality.getRandomPersonality()
        
        
        if self.cookie != None:
            try:
                getFlagUrl = self.teamIp+"/~contribute/cgi-bin/history.py?name="+self.cookie
                getFlagPage = pybrowse.Browser("http://" + getFlagUrl)
                getFlagPage.open()
            
                rawPage = getFlagPage.page
        
                successPattern = "address"
                successPtr = rawPage.find(successPattern)

                if successPtr < 0:
                    self.returnVal.setError()
                    return

                oldFlag = rawPage[successPtr+8:][:self.getFlagSize()]
                self.validatePreviousFlag(oldFlag)
                
            except Exception, e:
                self.output.write("got exception '%s' when getting flag" % (e))
                self.returnVal.setConnectFailed()
                return
        
        #set new flag
        try:
            randomName = self.getRandomString(random.randint(6,8))
            
            url = self.teamIp+"/~contribute/contribute.html"
        
            mainpg = pybrowse.Browser("http://" + url)
            mainpg.open()
            mainpg = mainpg.doRedirects()
            mainpg.parse()
            
            form = mainpg.forms[0]
            
            form.fields['name'] = randomName
            form.fields['address'] = self.getNewFlagText()
            form.fields['cc'] = str(random.randint(10000000,99999999))
            form.fields['contribution'] = str(random.randint(1,9999))
            
            resultPage = form.click(None).page
            
            successPattern = "Your contribution id"
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
            #try:
                getFlagUrl = self.teamIp+"/~contribute/cgi-bin/history.py?name="+self.cookie
                getFlagPage = pybrowse.Browser("http://" + getFlagUrl)
                getFlagPage.open()
            #except:
              #  pass
    
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return ContributeScoringScript