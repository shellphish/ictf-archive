import os, random, time, sys, string, re, socket, urllib

from ImageScripts.BaseScoringScript import BaseScoringScript 
from ImageScripts.Utility import pybrowse, browserpersonality

candidates = ['blitzkrieg', 'stallone', 'schtrappe', 'blix', 'schmidt']
class PollitScoringScript(BaseScoringScript):

    def doScoring(self):
        #get old flag  
        if self.cookie != None:
            try:
                name,id = self.cookie.split(":")
                
                personality = browserpersonality.getRandomPersonality()
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/~pollit/pollit.html", personality)
                mainpg.open()
                mainpg.parse()
                
                getPollForm = mainpg.forms[1]
                getPollForm.fields['username'] = name
                getPollForm.fields['pollid'] = id
                resultPage = getPollForm.click(None)
                
                successPtr = resultPage.page.find("-1")

                if successPtr != -1:
                    oldFlag = resultPage.page[successPtr+3:][:self.getFlagSize()]
                    self.validatePreviousFlag(oldFlag)
                else:
                    self.returnVal.setGetFlagFailed()

            except Exception, e:
                self.output.write("got exception %s getting flag" % (e))
                self.returnVal.setError()
        
        #set the new flag
        try:
            personality = browserpersonality.getRandomPersonality()
            mainpg = pybrowse.Browser("http://" + self.teamIp + "/~pollit/pollit.html", personality)
            mainpg.open()
            mainpg.parse()
                        
            name = self.getRandomString(random.randint(6,8))
            id = self.getRandomAlphaNum(6)
            
            createPollForm = mainpg.forms[0]
            
            for candidate in candidates:
                createPollForm.fields[candidate] = str(random.randint(1,100))
            
            flag = random.choice(candidates)
            createPollForm.fields[flag] = "-1 "+self.getNewFlagText()
            
            createPollForm.fields['username'] = name
            createPollForm.fields['pollid'] = id

            resultPage = createPollForm.click(None)
            
            successPtr = resultPage.page.find("saved.")
            if successPtr == -1:
                self.returnVal.setPostFlagFailed()
                return
            
            self.cookie = name+":"+id
            self.returnVal.setSuccess()

        except Exception, e:
            self.returnVal.setError()
            self.output.write("got exception %s setting new flag" % (e))
    
    def exerciseService(self):
        try:
            personality = browserpersonality.getRandomPersonality()
            mainpg = pybrowse.Browser("http://" + self.teamIp + "/~pollit/pollit.html", personality)
            mainpg.open()
            mainpg.parse()
                
            globalPoll = mainpg.forms[3]
            globalPoll.click(None)
        except:
            pass

        
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return PollitScoringScript