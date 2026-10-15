import os, random, time, sys, string, re, socket, urllib

from ImageScripts.BaseScoringScript import BaseScoringScript 
from ImageScripts.Utility import pybrowse, browserpersonality

class FeedbackScoringScript(BaseScoringScript):

    def doScoring(self):
        
        #get old flag  
        if self.cookie != None:
            try:
                name = self.cookie
                
                personality = browserpersonality.getRandomPersonality()
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/~feedback/cgi-bin/candidates.php", personality)
                mainpg.open()
                mainpg.parse()
            
                candidate = random.randint(0,4)
                
                feedbackForm = mainpg.forms[candidate]
                feedbackForm.fields['name'] = name
                feedbackForm.fields['comment'] = self.getRandomString(5) + " " + self.getRandomString(random.randint(4,9)) + random.choice(['?','.','!'])
                
                resultPage = feedbackForm.click(None)
                
                successPtr = resultPage.page.find("About")

                if successPtr != -1:
                    oldFlag = resultPage.page[successPtr+9:][:self.getFlagSize()]
                    self.validatePreviousFlag(oldFlag)
                else:
                    self.returnVal.setGetFlagFailed()

            except Exception, e:
                self.output.write("got exception %s getting flag" % (e))
                self.returnVal.setError()
        
        #set the new flag
        try:
            personality = browserpersonality.getRandomPersonality()
            mainpg = pybrowse.Browser("http://" + self.teamIp + "/~feedback/cgi-bin/candidates.php", personality)
            mainpg.open()
            mainpg.parse()
            
            candidate = random.randint(0,4)
            feedbackForm = mainpg.forms[candidate]
                 
            name = self.getRandomString(random.randint(6,8)) 
            feedbackForm.fields['name'] = name
            feedbackForm.fields['comment'] = self.getNewFlagText()
            
            resultPage = feedbackForm.click(None)
            
            successPtr = resultPage.page.find("feedback so far")
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
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/~feedback/cgi-bin/candidates.php", personality)
                mainpg.open()
                mainpg.parse()
            
                candidate = random.randint(0,4)
                
                feedbackForm = mainpg.forms[candidate]
                feedbackForm.fields['name'] = name
                feedbackForm.fields['comment'] = self.getRandomString(5) + " " + self.getRandomString(random.randint(4,9)) + random.choice(['?','.','!'])
                
                resultPage = feedbackForm.click(None)
            except:
                pass
        
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return FeedbackScoringScript