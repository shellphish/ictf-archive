import os, random, time, sys, string, re, socket, urllib

from ImageScripts.BaseScoringScript import BaseScoringScript 
from ImageScripts.Utility import pybrowse, browserpersonality

class DiebaldScoringScript(BaseScoringScript):

    def doScoring(self):
        #get old flag  
        if self.cookie != None:
            try:
                name,password = self.cookie.split(":")
                
                personality = browserpersonality.getRandomPersonality()
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/~diebald/cgi-bin/admin", personality)
                mainpg.open()
                mainpg.parse()
            
                getTaskForm = mainpg.forms[2]
                getTaskForm.fields['username'] = name
                getTaskForm.fields['password'] = password                
                resultPage = getTaskForm.click(None)
                
                successPtr = resultPage.page.find("pre")
                if successPtr != -1:
                    oldFlag = resultPage.page[successPtr+5:][:self.getFlagSize()]
                    self.validatePreviousFlag(oldFlag)
                else:
                    self.returnVal.setGetFlagFailed()

            except Exception, e:
                self.output.write("got exception %s getting flag" % (e))
                self.returnVal.setError()
        #set the new flag
        try:
            personality = browserpersonality.getRandomPersonality()
            mainpg = pybrowse.Browser("http://" + self.teamIp + "/~diebald/cgi-bin/admin", personality)
            mainpg.open()
            mainpg.parse()
                
            name = self.getRandomString(random.randint(6,8))
            password = self.getRandomAlphaNum(6)
            
            createUserForm = mainpg.forms[0]
            createUserForm.fields['username'] = name
            createUserForm.fields['password'] = password
            resultPage = createUserForm.click(None)
            
            successPtr = resultPage.page.find("Account successfully created")
            if successPtr == -1:
                self.returnVal.setPostFlagFailed()
                return
            
            addTaskForm = mainpg.forms[1]
            addTaskForm.fields['username'] = name
            addTaskForm.fields['password'] = password
            addTaskForm.fields['task'] = self.getNewFlagText()
            resultPage = addTaskForm.click(None)
            
            successPtr = resultPage.page.find("was assigned to user")
            if successPtr == -1:
                self.returnVal.setPostFlagFailed()
                return
            
            self.cookie = name+":"+password
            self.returnVal.setSuccess()
        except Exception, e:
            self.returnVal.setError()
            self.output.write("got exception %s setting new flag" % ( e ))
    
    def exerciseService(self):
        if self.cookie != None:
            try:
                name,password = self.cookie.split(":")
                
                personality = browserpersonality.getRandomPersonality()
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/~diebald/cgi-bin/admin", personality)
                mainpg.open()
                mainpg.parse()
            
                getTaskForm = mainpg.forms[2]
                getTaskForm.fields['username'] = name
                getTaskForm.fields['password'] = password                
                resultPage = getTaskForm.click(None)
            except:
                pass
        
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return DiebaldScoringScript