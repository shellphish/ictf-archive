import ftplib, os

from ImageScripts.BaseScoringScript import BaseScoringScript 
from ImageScripts.Utility import pybrowse, browserpersonality

class FtpScoringScript(BaseScoringScript):

    def flagCallback(self,line):
        self.validatePreviousFlag(line)
        
    def doScoring(self):
        try:
            #Login to ftp
            ftp = ftplib.FTP(self.teamIp)
            ftp.login() 
            ftp.cwd("/home/ftp/incoming")
        
            if self.cookie != None:
                ftp.retrlines("RETR "+self.cookie,self.flagCallback)
            
            #set new flag
        
            filename = self.getRandomString(9)
            
            file = open(filename,'w')
            file.write(self.getNewFlagText())
            file.close();
            
            file = open(filename,'r')
            ftp.storlines("stor "+filename,file)
            file.close()
            
            os.remove(filename)
            self.cookie = filename
            self.returnVal.setSuccess()
        
        except Exception, e:
            self.returnVal.setPostFlagFailed()
            self.output.write("got exception %s setting new flag" % (e))
       
    def exerciseService(self):
        pass
        
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return FtpScoringScript