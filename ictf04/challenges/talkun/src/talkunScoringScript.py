import os, random, time, sys, string, re, socket, urllib

from ImageScripts.BaseScoringScript import BaseScoringScript 
from ImageScripts.Utility import pybrowse, browserpersonality

class TalkunScoringScript(BaseScoringScript):
 
    def doScoring(self):
        #get old flag  
        if self.cookie != None:
            try:
                name = self.cookie
                personality = browserpersonality.getRandomPersonality()
                resultPage = pybrowse.Browser("http://" + self.teamIp + ":8081/notes?username="+name, personality)
                resultPage.open();
                
                successPtr = resultPage.page.find("["+name+":")
                
                if successPtr != -1:
                    oldFlag = resultPage.page[successPtr+len(name)+2:][:self.getFlagSize()]
                    self.validatePreviousFlag(oldFlag)
                else:
                    self.returnVal.setGetFlagFailed()
                
            except Exception, e:
                self.output.write("got exception %s getting flag" % (e))
                self.returnVal.setError()
     
        #set the new flag
        try:
            personality = browserpersonality.getRandomPersonality()
            login = pybrowse.Browser("http://" + self.teamIp + ":8081/login", personality)
            login.open()
            login.parse()
            
            loginForm = login.forms[0]
            
            name = self.getRandomString(random.randint(6,8))
            password = self.getRandomAlphaNum(6)
            
            loginForm.fields['username'] = name
            loginForm.fields['password'] = password
            
            resultPage = loginForm.click(None)
            resultPage.parse()
            

            successPtr = resultPage.page.find("Login succeeded")
            if successPtr == -1:
                self.returnVal.setPostFlagFailed()
                return
            
            notes = resultPage.click(resultPage.links[0])
            notes.parse()

            noteForm = notes.forms[0]
            
            noteForm.fields['note'] = self.getNewFlagText()
            noteForm.fields['line'] = str(random.randint(1,100))
            noteForm.fields['character'] = str(random.randint(1,20))
            
            resultPage = noteForm.click(None)
            
            successPtr = resultPage.page.find("Note accepted")
            if successPtr == -1:
                self.returnVal.setPostFlagFailed()
                return
         
            self.cookie = name
            self.returnVal.setSuccess()

        except Exception, e:
            self.returnVal.setError()
            self.output.write("got exception %s setting new flag" % (e))
    
    def exerciseService(self):
        if self.cookie != None:
            try:
                name = self.cookie
                personality = browserpersonality.getRandomPersonality()
                resultPage = pybrowse.Browser("http://" + self.teamIp + ":8081/notes?username="+name, personality)
                resultPage.open()
            except:
                pass
                
        
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return TalkunScoringScript