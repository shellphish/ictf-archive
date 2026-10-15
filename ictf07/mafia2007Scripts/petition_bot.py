#!/usr/bin/python

"""

http://<server>/~petition/cgi-bin/petition.py?first=john&last=doe&email=john@doe.com&comment=<flag>&id=

This stores a new flag and generate an ID

http://<server>/~petition/cgi-bin/petition.py?first=&last=&email=&comment=&id=<id>

This will print the stored flag, given the ID


"""

import os, random, time, sys, string, re, socket, urllib

import ImageScripts.BaseScoringScript as scoringScript
from ImageScripts.Utility import pybrowse, browserpersonality

class petitionScoringScript(scoringScript.BaseScoringScript):
    
    def doScoring(self): 
        # get old flag
        retFlag = None
        
        if self.cookie != "":
            try:
                personality = browserpersonality.getRandomPersonality()
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site/Petition.html")
                mainpg.open()
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site//Petition_files/widget1_markup.html")
                mainpg.open()
                mainpg.parse()
 
                adminForm = mainpg.forms[0]
                adminForm.fields["comment"] = "" 
                adminForm.fields["id"]  = self.cookie
                resultingPage = adminForm.click( None )
                resultingPage = resultingPage.doRedirects()
                successPtr = resultingPage.page.find("Your comment was:")
                if successPtr != -1:
                    self.validatePreviousFlag(resultingPage.page[successPtr+18:][:self.getFlagSize()])
                else:
                    pass
                
            except Exception, e:
                self.output.write("got exception %s getting flag" % (e))
                self.returnVal.setError()
                return
        
        # set the new flag
        try:
            personality = browserpersonality.getRandomPersonality()
            mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site/Petition.html")
            mainpg.open()
            mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site//Petition_files/widget1_markup.html")
            mainpg.open()
            mainpg.parse()

            myform = mainpg.forms[0]
            myform.fields["first"] = self.getRandomString(random.randint(4,10))
            myform.fields["last"] = self.getRandomString(random.randint(4,10))
            myform.fields["email"] = self.getRandomEmail()
            myform.fields["comment"] = self.getNewFlagText()

            myform.fields["id"] = ""
            resultingPage = myform.click( None )
            resultingPage = resultingPage.doRedirects()
            successPtr = resultingPage.page.find( "Your ID is " )
        
            if successPtr == -1:
                self.returnVal.setPostFlagFailed()
                return    
            else:
                self.cookie = resultingPage.page[successPtr+11:][:8]
                self.returnVal.setSuccess()
        
        except Exception, e:
            self.output.write("got exception %s setting new flag" % (e))
            self.returnVal.setError()
        
    def exerciseService( self ):
        pass

def getScoringScript():
    """
    this must be defined in every scoring module.
    """
    return petitionScoringScript