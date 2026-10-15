#!/usr/bin/python

"""
http://<server>/~wouldyou/cgi-bin/wouldyou.py
(POST)
name=<id>&steal=<flag>

This stores a new flag under ID <id>

http://<server>/~wouldyou/cgi-bin/wouldyou.py
(POST)
name=<id>&steal=<flag>

This stores a new flag under ID <id>
and returns the value of the previous flag.

"""


import os, random, time, sys, string, re, socket, urllib

import ImageScripts.BaseScoringScript as scoringScript
from ImageScripts.Utility import pybrowse, browserpersonality

class wouldYouScoringScript(scoringScript.BaseScoringScript):
                
    def doScoring(self):
        # get old flag
        if self.cookie != None:
            try:
                personality = browserpersonality.getRandomPersonality()
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site/Would_you.html")
                mainpg.open()
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site//Would_you_files/widget1_markup.html")
                mainpg.open()
                mainpg.parse()
    
                qForm = mainpg.forms[0]
                qForm.fields["q1"] = random.choice(("yes", "no")) 
                qForm.fields["q2"] = random.choice(("yes", "no")) 
                qForm.fields["q3"] = random.choice(("yes", "no")) 
                qForm.fields["q5"] = random.choice(("yes", "no")) 
                qForm.fields["q6"] = random.choice(("yes", "no")) 
                qForm.fields["q7"] = random.choice(("yes", "no")) 
                qForm.fields["steal"] =  self.getNewFlagText()
                qForm.fields["signature"] = self.cookie 
                resultingPage = qForm.click( None )
                resultingPage = resultingPage.doRedirects( )
                successPtr = resultingPage.page.find("choice was:")
                if successPtr != -1:
                    self.validatePreviousFlag(resultingPage.page[successPtr+12:][:self.getFlagSize()])
            except Exception, e:
                self.output.write("got exception %s getting flag" % (e))
                self.returnVal.setError()
                return
                
        # set the new flag
        try:
            personality = browserpersonality.getRandomPersonality()
            mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site/Would_you.html")
            mainpg.open()
            mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site//Would_you_files/widget1_markup.html")
            mainpg.open()
            mainpg.parse()
            
            qForm = mainpg.forms[0]
            qForm.fields["q1"] = random.choice(("yes", "no")) 
            qForm.fields["q2"] = random.choice(("yes", "no")) 
            qForm.fields["q3"] = random.choice(("yes", "no")) 
            qForm.fields["q5"] = random.choice(("yes", "no")) 
            qForm.fields["q6"] = random.choice(("yes", "no")) 
            qForm.fields["q7"] = random.choice(("yes", "no")) 

            self.cookie = self.getRandomString(random.randint(3,10))
            qForm.fields["steal"] =  self.getNewFlagText()
            qForm.fields["signature"] = self.cookie
            resultingPage = qForm.click(None)
            resultingPage = resultingPage.doRedirects()
   
            successPtr = resultingPage.page.find("was successfully saved.")
            if successPtr == -1:
                print "error cannot set flag"
                self.returnVal.setPostFlagFailed()
                return
            
        except Exception, e:
            self.output.write("got exception %s getting flag" % (e))
            self.returnVal.setError()
            return
        
        self.returnVal.setSuccess()
        
    def exerciseService( self ):

        if random.choice(("yes", "no")) == "yes":
            try:
                personality = browserpersonality.getRandomPersonality()
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site/Would_you.html")
                mainpg.open()
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site//Would_you_files/widget1_markup.html")
                mainpg.open()
                mainpg.parse()
                qForm = mainpg.forms[0]
                qForm.fields["q1"] = "yes" 
                qForm.fields["q2"] = "yes" 
                qForm.fields["q3"] = "yes" 
                qForm.fields["q4"] = "yes" 
                qForm.fields["q5"] = "yes" 
                qForm.fields["q6"] = "yes" 
                qForm.fields["q7"] = "yes" 
                qForm.fields["steal"] =  self.getRandomString(random.randint(3,10))
                qForm.fields["signature"] = self.getRandomString(random.randint(3,10))
                resultingPage = qForm.click( None )
                resultingPage = resultingPage.doRedirects( )
        
                successPtr = resultingPage.page.find("was successfully saved.")
                if successPtr == -1:
                    self.returnVal.setError()
                    return
                
                resultingPage.parse()
                qForm = resultingPage.forms[0]
                qForm.fields["first"] =  self.getRandomString(random.randint(3,10))
                qForm.fields["last"] = self.getRandomString(random.randint(3,10))
                qForm.fields["email"] = self.getRandomEmail()
                qForm.fields["name"] = self.getRandomString(random.randint(3,10))
                resultingPage = qForm.click( None )
                resultingPage = resultingPage.doRedirects( )
                
            except Exception, e:
                pass

def getScoringScript():
    """
    this must be defined in every scoring module.
    """
    return wouldYouScoringScript