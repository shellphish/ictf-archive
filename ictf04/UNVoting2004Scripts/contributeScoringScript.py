import os, random, time, sys, string, re, socket, urllib

from ImageScripts.BaseScoringScript import BaseScoringScript 
from ImageScripts.Utility import pybrowse, browserpersonality

candidates = ['blitzkrieg', 'stallone', 'schtrappe', 'blix', 'schmidt']

class ContributeScoringScript(BaseScoringScript):

    def doScoring(self):
        
        #get old flag
        
        if self.cookie != None:
            try:
                cc = self.cookie
                
                personality = browserpersonality.getRandomPersonality()
                resultPage = pybrowse.Browser("http://" + self.teamIp + "/~support/"+cc+".php", personality)
                resultPage.open()
                resultPage.parse()
                
                successPtr = resultPage.page.find("(")

                if successPtr != -1:
                    oldFlag = resultPage.page[successPtr+1:][:self.getFlagSize()]
                    self.validatePreviousFlag(oldFlag)
                else:
                    self.returnVal.setGetFlagFailed()
        
            except Exception, e:
                self.output.write("got exception %s getting flag" % (e))
                self.returnVal.setError()
        
        #set the new flag
        try:
            candidate = random.choice(['Blitzkrieg','Stallone','Schtrappe','Schmidt','Blix'])
            cc = str(random.randint(10000000,99999999))
            amount = str(random.randint(1,9999))
            comment = self.getNewFlagText()
            
            setFlagUrl = self.teamIp+"/~support/cgi-bin/donate.py?candidate="+candidate+"&cc="+cc+"&amount="+amount+"&comment="+comment
            mainpg = pybrowse.Browser("http://" + setFlagUrl)
            mainpg.open()
            
            successPtr = mainpg.page.find("Thank you very much")
            if successPtr == -1:
                self.returnVal.setPostFlagFailed()
                return
            
            self.cookie = cc
            self.returnVal.setSuccess()
           
        except Exception, e:
            self.returnVal.setError()
            self.output.write("got exception %s setting new flag" % (e))
    
    def exerciseService(self):
        try:
            if self.cookie != None:
                cc = self.cookie
                        
                personality = browserpersonality.getRandomPersonality()
                resultPage = pybrowse.Browser("http://" + self.teamIp + "/~support/"+cc+".php", personality)
                resultPage.open()
                resultPage.parse()
        except:
            pass
        
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return ContributeScoringScript