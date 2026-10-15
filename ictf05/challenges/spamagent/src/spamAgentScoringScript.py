import httplib
import urllib
import random
import re

from ImageScripts.BaseScoringScript import BaseScoringScript 
from ImageScripts.Utility import pybrowse, browserpersonality

class SpamAgentScoringScript(BaseScoringScript):
    
    def postAgentText(self, agentText):
        url = self.teamIp+"/~spamagent/spamagent.html"
        
        mainpg = pybrowse.Browser("http://" + url)
        mainpg.open()
        mainpg = mainpg.doRedirects()
        mainpg.parse()
            
        form = mainpg.forms[0]
           
        form.fields['script'] = agentText
        resultPage = form.click(None).page
        
        return resultPage
    
    def doScoring(self): 
        """
        this is the entry point for the scoring script.
        """
        
        personality = browserpersonality.getRandomPersonality()
        
        if self.cookie != None:
            try:
                name,password = self.cookie.split(":")
                
                senderText = "<sender><user>"+name+"</user><password>"+password+"</password></sender>"
                codeText = "<code>set flag [store get flag]; results set $flag</code>"
                agentText = "<agent>\n" + senderText +"\n"+codeText+"\n</agent>"
                
                resultPage = self.postAgentText(agentText)
                
                oldFlag = resultPage[:self.getFlagSize()]
                self.validatePreviousFlag(oldFlag)
                
            except Exception, e:
                self.output.write("got exception '%s' when getting flag" % (e))
                self.returnVal.setConnectFailed()
                return
        
        #set new flag
        try:
            name = self.getRandomString(random.randint(6,8))
            password = self.getRandomAlphaNum(8)
            
            senderText = "<sender><user>"+name+"</user><password>"+password+"</password></sender>"
            codeText = "<code>store set flag \""+self.getNewFlagText()+"\"; results set \"Flag was set\";</code>"
            
            agentText = "<agent>\n" + senderText +"\n"+codeText+"\n</agent>"
             
            resultPage = self.postAgentText(agentText)
            
            successPattern = "Flag was set"
            successPtr = resultPage.find(successPattern)

            if successPtr < 0:
                self.returnVal.setPostFlagFailed()
                return
            
            self.cookie = name+":"+password
            self.returnVal.setSuccess()
            
        except Exception, e:
            self.output.write("got exception '%s' when setting flag" % (e))
            self.returnVal.setError()
            return
    
    def exerciseService(self):
        pass
    
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return SpamAgentScoringScript