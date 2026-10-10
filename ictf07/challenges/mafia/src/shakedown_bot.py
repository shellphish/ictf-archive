#!/usr/bin/python

# shakedown scoring script.
# 
# Flags are stored by sending a message from the boss to one of his
# artists.
# Flags are read by logging in as an artist and checking the messages

import os, random, time, sys, string, re

import ImageScripts.BaseScoringScript as scoringScript
from ImageScripts.Utility import pybrowse, browserpersonality

countries = ["US", "Italy", "Germany", "India", "UK", "Austria", "France", "Canada", "test", "blah"]

titles = ["Message", "test", "Test", "Title", "you have mail", "important"]

class shakedownScoringScript(scoringScript.BaseScoringScript):
    
    def getRandomCountry(self):
        """get a random country name. 
           used during the generation of new artist users."""
        return countries[random.randint(0, len(countries) - 1)]
    
    def getRandomTitle(self):
        """get a random message title.
           used during the generation of new messages."""
        return titles[random.randint(0, len(titles) - 1)]
    
    def checkError(self,page):
        errorPtr = page.page.find("Traceback")
        if errorPtr != -1:
            self.returnVal.setError()
            sys.exit(-1)
        
        errorPtr = page.page.find("following error")
        if errorPtr != -1:
            self.returnVal.setError()
            sys.exit(-1)
        
    
    def doScoring(self):
        myPort = "4242"
        oldFlag = None
        
        # get old flag
        if self.cookie != None:
            artist_name, artist_pwd = self.cookie.split(":")
        
            try:
                personality = browserpersonality.getRandomPersonality()
                
                # 1. go to the main page
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site/Bosses_and_artists.html")
                mainpg.open()
        
                # 2. login as an artist
                mainpg = pybrowse.Browser("http://" + self.teamIp  + ":" + myPort + "/artists/login/")
                mainpg.open()
                mainpg.parse()

                adminForm = mainpg.forms[0]
                adminForm.fields["username"] = artist_name
                adminForm.fields["password"] = artist_pwd
                resultingPage = adminForm.click( None )
                resultingPage = resultingPage.doRedirects( )
                resultingPage.parse()
                successPtr = resultingPage.page.find("Confirmation number:")
                
                if successPtr != -1:
                    oldFlag = resultingPage.page[successPtr + 21:][:self.getFlagSize()]
                
                self.validatePreviousFlag(oldFlag)

            except Exception, e:
                self.output.write("got exception %s getting flag" % (e))
                self.returnVal.setError()
                return
        
        # set the new flag
        try:
            personality = browserpersonality.getRandomPersonality()
        
            # 1. go to the shell's page
            mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site/Bosses_and_artists.html")
            mainpg.open()
        
            # 2. create a new boss
            mainpg = pybrowse.Browser("http://" + self.teamIp + ":" + myPort + "/bosses/new/")
    
            mainpg.open()
            mainpg.parse()
            
            myform = mainpg.forms[0]

            boss_name = self.getRandomString(random.randint(6,16))
            boss_pwd = self.getRandomString(random.randint(6,8))
            
            myform.fields["name"] = boss_name.capitalize()
            myform.fields["username"] = boss_name
            myform.fields["password"] = boss_pwd
            myform.fields["password_again"] = boss_pwd
            
            resultingPage = myform.click( None )
            resultingPage = resultingPage.doRedirects( )
            resultingPage.parse()
            
            self.checkError(resultingPage)
        
            # resulting page should be /bosses/view/N/
            boss_id = resultingPage.documentroot.split("/")[3]
            
            # 3. create a new artist and link it to the boss
            mainpg = pybrowse.Browser("http://" + self.teamIp + ":" + myPort  + "/artists/new/")
            mainpg.open()

            mainpg.parse()
            successPtr = mainpg.page.find("option value=\"" + boss_id)
            if successPtr == -1:
                self.returnVal.setError()
                return
                
            mainpg.forms[0].addField("boss", boss_id)
            myform = mainpg.forms[0]

            artist_name = self.getRandomString(random.randint(6,16))
            artist_pwd = self.getRandomString(random.randint(6,8))
            
            myform.fields["name"] = artist_name.capitalize()
            myform.fields["username"] = artist_name
            myform.fields["password"] = artist_pwd
            myform.fields["password_again"] = artist_pwd
            myform.fields["country"] = self.getRandomCountry()

            resultingPage = myform.click( None )
            resultingPage = resultingPage.doRedirects()
            resultingPage.parse()
        
            self.checkError(resultingPage)
        
            # 4. login as the initial boss
            mainpg = pybrowse.Browser("http://" + self.teamIp + ":" + myPort + "/bosses/login/")
            mainpg.open()
            mainpg.parse()
            myform = mainpg.forms[0]
            myform.fields["username"] = boss_name
            myform.fields["password"] = boss_pwd
            resultingPage = myform.click( None )
            resultingPage = resultingPage.doRedirects()
            resultingPage.parse()
        
            # 5. click on the protection link and set flag
            resultingPage = resultingPage.click(resultingPage.links[10])
            resultingPage.doRedirects()
            resultingPage.parse()

            myform = resultingPage.forms[0]
            myform.fields["news-title"] = self.getRandomTitle()
            myform.fields["news-content"] = "Confirmation number: " + self.getNewFlagText()
            myform.fields["news-revenue"] = random.randint(0, 1000000)
            resultingPage = myform.click( "news" )
            resultingPage = resultingPage.doRedirects()
            resultingPage.parse()
        
            self.checkError(resultingPage)
        
            self.cookie = artist_name + ":" + artist_pwd
            self.returnVal.setSuccess()
        
        except Exception, e:
            self.output.write("got exception %s setting new flag" % (e))
            self.returnVal.setError()
            return
    
    def exerciseService( self ):
        self.returnVal.setSuccess()
        
def getScoringScript():
    """
    this must be defined in every scoring module.
    """
    return shakedownScoringScript