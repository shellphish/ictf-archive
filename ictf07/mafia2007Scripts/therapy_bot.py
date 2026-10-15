#!/usr/bin/python

import os, random, time, traceback, sys, string

import ImageScripts.BaseScoringScript as scoringScript
from ImageScripts.Utility import pybrowse, browserpersonality

retFlag = ""
retCookie = ""
myHost = ""
port = "8080"

#name alphabet
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
           'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
           's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
           'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
           'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z' ]

domains = ["com", "edu", "org", "au", "biz"]

class therapyScoringScript(scoringScript.BaseScoringScript):
    
    def getRandomString(self,len):
        ret = ""
        for i in range(len):
            ret += random.choice(alphabet)
        return ret
    
    def getRandomEmail(self):
        ret = self.getRandomString(random.randint(4,8)) + "@" + self.getRandomString(random.randint(3,8)) + "." + self.getRandomString(random.randint(3,8)) + "." + random.choice(domains)
    
        return ret
    
    def doLogin(self,user, passwd): 
        mainpg = pybrowse.Browser("http://" + myHost + "/Therapy/login.do")
        mainpg.open()
        mainpg.parse()
        loginForm = mainpg.forms[0]
        loginForm.fields['username'] = user
        loginForm.fields['password'] = passwd
        resultPage = loginForm.click(None)
        resultPage = resultPage.doRedirects( )
        
        resultPage.parse()
        rawPage = resultPage.page
        successPtr = rawPage.find("Logout")
        
        if successPtr < 0:
            self.returnVal.setError()
            sys.exit(2)
        
        return resultPage
    
    def createAccount(self, name, passwd, role):
        global myHost
        
        mainpg = pybrowse.Browser("http://" + myHost + "/Therapy/createuser.do?role=" + role)
        mainpg.open()
        mainpg.parse()
        
        userform = mainpg.forms[0]
        userform.fields['firstname'] = self.getRandomString(random.randint(4,10))
        userform.fields['lastname'] = self.getRandomString(random.randint(5,10))
        userform.fields['email'] = self.getRandomEmail()
        userform.fields['username'] = name
        userform.fields['password'] = passwd
        userform.fields['role'] = role
        resultPage = userform.click("submit")
        resultPage = resultPage.doRedirects( )
        return resultPage
    
    
    def doScoring(self):
        global myHost
        
        myHost = self.teamIp + ":" + port
    
        username = ""
        password = ""
        
        # get old flag
        if self.cookie != None:
            try:
                
                if self.cookie.find( ':' ) != -1:
                    username, password = self.cookie.split(":")
            
                personality = browserpersonality.getRandomPersonality()
                mainpg = pybrowse.Browser("http://" + myHost + "/Therapy/")
                mainpg.open()
                mainpg.parse()
                
                if mainpg.containsLink("/Therapy/login.do") == None:
                    self.output.write("Something is wrong: no login.do link is found on the front page")
                    self.returnVal.setError()
                    return
            
                resultPage = self.doLogin(username, password)
                # view user's private information
                resultPage = resultPage.click(resultPage.links[9])
                resultPage.doRedirects()
                rawPage = resultPage.page
                successPtr = rawPage.find("addinfo")
                if successPtr < 0:
                    self.returnVal.setGetFlagFailed()
                
                oldFlag = rawPage[successPtr + 21:][:self.getFlagSize()]
                self.validatePreviousFlag(oldFlag)
                
                # logout 
                resultPage.parse()
                resultPage = resultPage.click(resultPage.links[10])
                resultPage.doRedirects()
                
                
            except Exception, e:
                self.output.write("got exception when getting flag: \n" + ''.join(traceback.format_exception(Exception, e, sys.exc_info( )[2])))
                self.returnVal.setError()
    
        try:
            personality = browserpersonality.getRandomPersonality()
            mainpg = pybrowse.Browser("http://" + myHost + "/Therapy/")
            mainpg.open()
            mainpg.parse()
            
             # create a new user account
            username = self.getRandomString(random.randint(6,10))
            password = self.getRandomString(random.randint(4,10))

            resultPage = self.createAccount(username, password, "client")
            
            # login using the new account
            resultPage = self.doLogin(username, password)
            resultPage.parse()
            
            # go to story submission page
            resultPage = resultPage.click(resultPage.links[9])
            resultPage = resultPage.doRedirects()
            resultPage.parse()
            
            #print resultPage.page
            storyform = resultPage.forms[0]
            storyform.fields['story'] = "This is way too sad ..";
            storyform.fields['addinfo'] = self.getNewFlagText()
            resultPage = storyform.click("submit")
            resultPage = resultPage.doRedirects( )
            
            rawPage = resultPage.page
            successPtr = rawPage.find("View or edit")
            if successPtr < 0:
                self.returnVal.setPostFlagFailed()
                return
            
            resultPage.parse()
            
            # go and view the submitted info
            resultPage = resultPage.click(resultPage.links[9])
            resultPage = resultPage.doRedirects()
            rawPage = resultPage.page
            successPtr = rawPage.find("addinfo")
            if successPtr < 0:
                print "Failed to retrieve a flag"
                self.returnVal.setPostFlagFailed()
                return
            
            resultPage.parse()
            
             # logout 
            if resultPage.containsLink("/Therapy/logout.do"):
                resultPage = resultPage.click("/Therapy/logout.do")
                resultPage = resultPage.doRedirects()
            else:
                self.returnVal.setError()
                return
        
            self.cookie = username + ":" + password
            self.returnVal.setSuccess()
            return
        
        except Exception, e:
            self.output.write("got exception when setting flag: \n" + ''.join(traceback.format_exception(Exception, e, sys.exc_info()[2])))
            self.returnVal.setError()
            return

    # check other parts of the site
    def exerciseService( self ):
        global myHost
        myHost = self.teamIp + ":" + port
        
        doCheck = random.choice(("yes", "no"))
        if doCheck == "yes":
            username = self.getRandomString(random.randint(6,10))
            password = self.getRandomString(random.randint(4,10))
            resultPage = self.createAccount(username, password, "counselor")
            rawPage = resultPage.page
            
            successPtr = rawPage.find("Congratulations")
            if successPtr < 0:
                self.returnVal.setError()
                return
            resultPage.parse()
            
            resultPage = resultPage.click(resultPage.links[9])
            resultPage = resultPage.doRedirects()
            
            rawPage = resultPage.page
            successPtr = rawPage.find("Best Clients")
            if successPtr < 0:
                self.returnVal.setError()
                return
            resultPage.parse()
            
            if resultPage.containsLink("/Therapy/logout.do"):
                resultPage = resultPage.click("/Therapy/logout.do")
                resultPage = resultPage.doRedirects()
            else:
                self.returnVal.setError()
                return
        return 0

def getScoringScript():
    """
    this must be defined in every scoring module.
    """
    return therapyScoringScript
