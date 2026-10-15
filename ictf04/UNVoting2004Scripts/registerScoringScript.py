import os, random, time, sys, string, re, socket, urllib

from ImageScripts.BaseScoringScript import BaseScoringScript 
from ImageScripts.Utility import pybrowse, browserpersonality

months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

class RegisterScoringScript(BaseScoringScript):

    def doScoring(self):
             
        #get old flag
        if self.cookie != None:
            try:
                password, wwid = self.cookie.split(':')
                
                personality = browserpersonality.getRandomPersonality()
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/~register/register.html", personality)
                mainpg.open()
                mainpg.parse()
                
                reviewForm = mainpg.forms[1]
                reviewForm.fields["password"] = password 
                reviewForm.fields["wwid"]  = wwid
                
                resultingPage = reviewForm.click(None)
                resultingPage = resultingPage.doRedirects()
                
                successPtr = resultingPage.page.find("name=\"wwid\"")

                if successPtr != -1:
                    oldFlag = resultingPage.page[successPtr+19:][:self.getFlagSize()]
                    self.validatePreviousFlag(oldFlag)
                else:
                    self.returnVal.setGetFlagFailed()
                
            except Exception, e:
                self.output.write("got exception %s getting flag" % (e))
                self.returnVal.setError()
        
        #set the new flag
        try:
            personality = browserpersonality.getRandomPersonality()
            mainpg = pybrowse.Browser("http://" + self.teamIp + "/~register/register.html", personality)
            mainpg.open()
            mainpg.parse()
            
            registrationForm = mainpg.forms[0]
            
            password = self.getRandomAlphaNum(8)
            wwid = self.getNewFlagText()

            registrationForm.fields['first'] = self.getRandomString(random.randint(5,7))
            registrationForm.fields['last'] = self.getRandomString(random.randint(6,9))
            registrationForm.fields['dob'] = str(random.choice(months))+" "+str(random.randint(1,29))+", "+str(random.randint(1900,2000))
            registrationForm.fields['email'] = self.getRandomEmail()
            registrationForm.fields['password'] = password
            registrationForm.fields['wwid'] = wwid
            
            resultingPage = registrationForm.click(None)
            
            successPtr = resultingPage.page.find("Registration successful!")
            
            if successPtr == -1:
                self.returnVal.setPostFlagFailed()
                return
            
            self.cookie = password+":"+wwid
            
            self.returnVal.setSuccess()
           
        except Exception, e:
            self.returnVal.setError()
            self.output.write("got exception %s setting new flag" % (e))
    
    def exerciseService(self):
        if self.cookie != None:
            try:
                password, wwid = self.cookie.split(':')
                
                personality = browserpersonality.getRandomPersonality()
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/~register/register.html", personality)
                mainpg.open()
                mainpg.parse()
                
                reviewForm = mainpg.forms[1]
                reviewForm.fields["password"] = password 
                reviewForm.fields["wwid"]  = wwid
                
                resultingPage = reviewForm.click(None)
            except:
                pass
        
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return RegisterScoringScript