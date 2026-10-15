"""

https://<server>:4443/login? user=myname&password=miconsenta&operation=OP-store

this will "touch" the file "myname" and allow for the actual storing  of the flag which is done by

https://<server>:4443/store? filename=flagfile&content=flagcontent&user=myname

(note: the order of the parameters is IMPORTANT!)

To retrieve the file:

echo "flagfile" | nc -u <server> 2345

which will return

https://<server>:4443/flagfile
+flagcontent

"""

import os, random, time, sys, string, re, socket, urllib

from ImageScripts.BaseScoringScript import BaseScoringScript 
from ImageScripts.Utility import pybrowse, browserpersonality


#service ports
httpPort = 80
udpPort   = 2345

#constant form values
myPassword  = "miconsenta"
myOperation = "OP-store"
    
#timeout
udpResponseTimeout = 5

class SpamgenScoringScript(BaseScoringScript):

    def doScoring(self):      
        #get old flag
        if self.cookie != None:
            try:
                (uname, pwd) = self.cookie.split(':')
                personality = browserpersonality.getRandomPersonality()
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/~spamgen/cgi-bin/spamgen.py?action=read", personality, debug=0)
                mainpg.open()
                mainpg.parse()
                
                adminForm = mainpg.forms[0]
                adminForm.fields["uname"] = uname 
                adminForm.fields["pwd"]  = pwd
                
                resultingPage = adminForm.click(None)
                resultingPage = resultingPage.doRedirects( )
                
                successPtr = resultingPage.page.find( "</h3>" )
                
                if successPtr != -1:
                    oldFlag = resultingPage.page[successPtr+6:][:self.getFlagSize()]
                    self.validatePreviousFlag(oldFlag)

            except Exception, e:
                self.output.write("got exception %s getting flag" % (e))
        
        #set the new flag
        try:
            personality = browserpersonality.getRandomPersonality()
            mainpg = pybrowse.Browser("http://" + self.teamIp + "/~spamgen/cgi-bin/spamgen.py?action=upload", personality, debug=0)
            mainpg.open()
            mainpg.parse()
         
            randomName = self.getRandomString(10)

            adminForm = mainpg.forms[0]
            adminForm.fields["uname"] = randomName
            adminForm.fields["pwd"]  = myPassword
            adminForm.fields["thetext"] = self.getNewFlagText()
        
            resultingPage = adminForm.click(None)
            resultingPage = resultingPage.doRedirects()
        
            failPtr = resultingPage.page.find("uccess")
        
            if failPtr != -1:
                successPtr = resultingPage.page.find( "Your file has been saved" )
        
            self.cookie = randomName+':'+myPassword
        
            self.returnVal.setSuccess()
        
        except Exception, e:
            self.returnVal.setError()
            self.output.write("got exception %s setting new flag" % (e))
    
    def exerciseService(self):
        if self.cookie != None:
            try:
                (uname, pwd) = self.cookie.split(':')
                personality = browserpersonality.getRandomPersonality()
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/~spamgen/cgi-bin/spamgen.py?action=read", personality, debug=0)
                mainpg.open()
                mainpg.parse()
                
                adminForm = mainpg.forms[0]
                adminForm.fields["uname"] = uname 
                adminForm.fields["pwd"]  = pwd
                
                resultingPage = adminForm.click(None)
            except:
                pass
        
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return SpamgenScoringScript