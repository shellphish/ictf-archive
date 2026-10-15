import re
import random
import xmlrpclib
from ImageScripts.BaseScoringScript import BaseScoringScript 

hex = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A','B','C','D','E','F']

class SpamdbScoringScript(BaseScoringScript):
    
    def genUser(self):
        
        fn = ["john", "joe", "jake", "horst", "franz", "detlef", "dietmar", "ingeborg", "angela", "george", "otto", "kalle", "jenna","bob","frank"];
        ln = ["doe", "mueller", "meier", "schmidt", "bush", "kerry", "merkel", "smith", "heinze", "schroedinger"]
        dom = ["sex", "drugs", "school", "rock", "computer", "unix", "service", "online", "live", "download", "old", "buy", "shop", "beer", "bong", "root","leet"]
        tld = ["gov","net","edu","com","org","de","us","uk","su"]
        delim = [".", "", "-"]
        
        name = ""
        
        name += random.choice(fn)
        name += random.choice(delim)
        name += random.choice(ln)
        name += "@"
        
        d = random.choice(delim)
        y = random.randint(2,4)
        for i in range(0,y):
            name += random.choice(dom)
            if(i < y-1):
                name += d
        
        name += "."+random.choice(tld)

        return name
    
    def doScoring(self):
        """
        this is the entry point for the scoring script.
        """
        
        serverUrl = "http://"+self.teamIp+"/~spamdb/cgi-bin/server.php"
        server = xmlrpclib.Server(serverUrl)
        
        #Get old flag
        if self.cookie != None:
            try:
                user,password = self.cookie.split(":")
                oldFlag = server.spamdb.veryfy_data(user,password)
                self.validatePreviousFlag(oldFlag)
            except Exception, e:
                self.output.write("got exception '%s' when getting flag" % (e))
                self.returnVal.setError()
                
        #Set new flag
        try:
            user = self.genUser()
            password = server.spamdb.create_account(user)
            result = server.spamdb.upload_data(user, password, self.getNewFlagText())
            
            self.cookie = user + ":" + password
            
            if(result == "OK"):
                self.returnVal.setSuccess()
                
        except Exception, e:
            self.output.write("got exception '%s' when setting flag" % (e))
            self.returnVal.setError()
            return

    def exerciseService(self):
        pass
    
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return SpamdbScoringScript