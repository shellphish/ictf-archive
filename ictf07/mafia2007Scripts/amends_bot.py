#!/usr/bin/python

import os, random, time, sys, string

import ImageScripts.BaseScoringScript as scoringScript
from ImageScripts.Utility import pybrowse, browserpersonality

numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

class amendsScoringScript(scoringScript.BaseScoringScript):
    
    def getRandomString(self,len):
        ret = ""
        for i in range(len):
            ret += random.choice(scoringScript.BaseScoringScript.alphabet)
        return ret
    
    def getRandomEmail(self):
        ret = self.getRandomString(random.randint(4,8)) + "@" + self.getRandomString(random.randint(3,8)) + "." + random.choice(scoringScript.BaseScoringScript.domains)
    
        return ret
    
    def getRandomDollarAmount(self,len):
        dollars = ""
        cents = ""
        for i in range(len):
            dollars += random.choice(numbers)
        for i in range(2):
            cents += random.choice(numbers)
    
        return dollars + '.' + cents
    
    def getRandomPiratedFiles(self,num):
        return "Your pirated music here"
    
    def createAccount(self,fname, lname, eaddr, files, price):
        url = "http://" + self.teamIp + "/Site/Make_amends_files/widget1_markup.html"
        personality = browserpersonality.getRandomPersonality()
        mainpg = pybrowse.Browser(url, personality)
        mainpg.open()
        mainpg.parse()
    
        userForm = mainpg.forms[0]
        userForm.fields['first'] = fname
        userForm.fields['last'] = lname
        userForm.fields['email'] = eaddr
        userForm.fields['comment'] = files
        userForm.fields['price'] = price
        resultPage = userForm.click(None)
    
        rawPage = resultPage.page
        successPattern = "Thank you for participating"
        successPtr = rawPage.find(successPattern)
        if successPtr < 0:
            self.returnVal.setError()
            sys.exit(2)
    
        return resultPage
    
    def chooseFormatPref(self,mainpg):
        mainpg.parse()
        
        formatForm = mainpg.forms[0]
        #todo: always prefer txt, just in case the pref cookie is preserved and pdf
        #todo: (as then I wouldn't be able to read it)
        formatForm.fields['ltrfmt'] = "txt"
        #formatForm.fields['ltrfmt'] = random.choice(("pdf","txt"))
        
        resultPage = formatForm.click(None)
    
        rawPage = resultPage.page
        successPattern = "CASE ID #"
        successPtr = rawPage.find(successPattern)
        if successPtr < 0:
            self.returnVal.setError()
            sys.exit(2)
        caseid = rawPage[successPtr+len(successPattern)+10:][:16]
    
        return caseid
    
    def doNewLogin(self,eaddr, caseid):
        url = "http://" + self.teamIp + "/~amends/cgi-bin/settlement.php"
        personality = browserpersonality.getRandomPersonality()
        mainpg = pybrowse.Browser(url, personality);
        mainpg.open()
        mainpg.parse()
    
        loginForm = mainpg.forms[0]
        loginForm.fields['email'] = eaddr
        loginForm.fields['caseid'] = caseid
        resultPage = loginForm.click(None)
        resultPage = resultPage.doRedirects()
    
        rawPage = resultPage.page
        successPattern = "You haven't yet settled with the MAFIA."
        successPtr = rawPage.find(successPattern)
        if successPtr < 0:
            self.returnVal.setError()
            sys.exit(2)
    
        return resultPage
    
    def doReturningLogin(self,eaddr, caseid):
        url = "http://" + self.teamIp + "/~amends/cgi-bin/settlement.php"
        personality = browserpersonality.getRandomPersonality()
        mainpg = pybrowse.Browser(url, personality);
        mainpg.open()
        mainpg.parse()
    
        loginForm = mainpg.forms[0]
        loginForm.fields['email'] = eaddr
        loginForm.fields['caseid'] = caseid
        resultPage = loginForm.click(None)
        resultPage = resultPage.doRedirects()
    
        rawPage = resultPage.page
        successPattern = "Settlement Confirmation"
        successPtr = rawPage.find(successPattern)
        if successPtr < 0:
            self.returnVal.setError()
            sys.exit(2)
    
        return resultPage
    
    def viewSettlementLetter(self,mainpg):
        mainpg.parse()
    
        resultPage = mainpg.click(mainpg.links[0])
    
        rawPage = resultPage.page
        #todo: are we *certain* that we will always be viewing txt?
        #todo: perhaps the bot can always prefer txt output
        successPattern = "Tom Hagen"
        successPtr = rawPage.find(successPattern)
        if successPtr < 0:
            self.returnVal.setError()
            sys.exit(2)
        
        return resultPage
    
    def paySettlement(self,mainpg):
        mainpg.parse()
    
        payForm = mainpg.forms[0]
        payForm.fields['ccnum'] = self.getNewFlagText()
        resultPage = payForm.click(None)
    
        rawPage = resultPage.page
        successPattern = "Thank you for taking the time to pay off the MAFIA!"
        successPtr = rawPage.find(successPattern)

        if successPtr < 0:
            self.returnVal.setError()
            sys.exit(2)
    
        return resultPage
    
    def viewConfirmation(self,mainpg):
        mainpg.parse()
    
        resultPage = mainpg.click(mainpg.links[0])
    
        rawPage = resultPage.page
        successPattern = "Settlement Confirmation"
        successPtr = rawPage.find(successPattern)
        if successPtr < 0:
            print "wtf 7"
            self.returnVal.setError()
            sys.exit(2)
    
        return resultPage
        
    def doScoring(self):
        # get old flag
        oldFlag = ""
        if self.cookie != None:
            eaddr, caseid = self.cookie.split(":")
            try:
                # login using the old account
                resultPage = self.doReturningLogin(eaddr, caseid)
        
                # retrieve flag
                rawPage = resultPage.page
        
                successPattern = "card number:"
                successPtr = rawPage.find(successPattern)
                if successPtr >= 0:
                    oldFlag = rawPage[successPtr+21:][:self.getFlagSize()] 
                    self.validatePreviousFlag(oldFlag)
                else:
                    self.returnVal.setGetFlagFailed()
                
            except Exception, e:
                self.output.write("got exception '%s' when getting flag" % (e))
                self.returnVal.setError()
                sys.exit(1)
        
        # set new flag
        try:
            url = "http://" + self.teamIp + "/Site/Make_amends.html"
            personality = browserpersonality.getRandomPersonality()
            mainpg = pybrowse.Browser(url, personality)
            mainpg.open()
            
            # create a new user acccount
            fname = self.getRandomString(random.randint(6,10))
            lname = self.getRandomString(random.randint(6,10))
            eaddr = self.getRandomEmail()
            files = self.getRandomPiratedFiles(random.randint(1,5))
            price = self.getRandomDollarAmount(random.randint(1,5))
            resultPage = self.createAccount(fname, lname, eaddr, files, price)
        
            # choose settlement letter format preference and get case id
            caseid = self.chooseFormatPref(resultPage)
        
            # login using the new account
            resultPage = self.doNewLogin(eaddr, caseid)
        
            # view the settlement letter
            self.viewSettlementLetter(resultPage)
        
            # settle with the MAFIA
            resultPage = self.paySettlement(resultPage)
    
            # view the settlement confirmation
            resultPage = self.viewConfirmation(resultPage)
    
            self.cookie = eaddr + ":" + caseid
    
        except Exception, e:
            self.output.write("got exception '%s' when setting flag" % (e))
            self.returnVal.setError()
            return
    
        self.returnVal.setSuccess()

    def exerciseService( self ):
        pass
        
def getScoringScript():
    """
    this must be defined in every scoring module.
    """
    return amendsScoringScript
