import httplib
import urllib
import random
import re

from ImageScripts.BaseScoringScript import BaseScoringScript 
from ImageScripts.Utility import pybrowse, browserpersonality

class MuseumScoringScript(BaseScoringScript):
    
    def doScoring(self): 
        """
        this is the entry point for the scoring script.
        """
        
        personality = browserpersonality.getRandomPersonality()
        
        if self.cookie != None:
            try:
                first,last = self.cookie.split(":")

                getFlagUrl = self.teamIp+"/~museum/cgi-bin/museum_admin.pl?first="+first+"&last="+last+"&password=unbreakable"
                getFlagPage = pybrowse.Browser("http://" + getFlagUrl)
                getFlagPage.open()
            
                rawPage = getFlagPage.page
                
                oldFlag = rawPage[253:][:self.getFlagSize()]
                self.validatePreviousFlag(oldFlag)
                
            except Exception, e:
                self.output.write("got exception '%s' when getting flag" % (e))
                self.returnVal.setConnectFailed()
                return
        
        #set new flag
        try:
            first = self.getRandomString(random.randint(6,8))
            last = self.getRandomString(random.randint(6,8))
            
            idea = urllib.quote(self.getNewFlagText())
            
            setFlagUrl = self.teamIp+"/~museum/cgi-bin/museum_upload.pl?first="+first+"&last="+last+"&dob=&ssn=&mmn=&email=&idea="+idea
        
            mainpg = pybrowse.Browser("http://" + setFlagUrl)
            mainpg.open()
            resultPage = mainpg.page

            successPattern = "Your idea has been received!!"
            successPtr = resultPage.find(successPattern)

            if successPtr < 0:
                self.returnVal.setPostFlagFailed()
                return
            
            self.cookie = first+":"+last
            self.returnVal.setSuccess()

        except Exception, e:
            self.output.write("got exception '%s' when setting flag" % (e))
            self.returnVal.setError()
            return
    
    def exerciseService(self):
        if self.cookie != None:
            try:
                first,last = self.cookie.split(":")

                getFlagUrl = self.teamIp+"/~museum/cgi-bin/museum_admin.pl?first="+first+"&last="+last+"&password=unbreakable"
                getFlagPage = pybrowse.Browser("http://" + getFlagUrl)
                getFlagPage.open()
            except:
                pass
    
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return MuseumScoringScript