import os, random, time, sys, string, socket

from ImageScripts.BaseScoringScript import BaseScoringScript 

good_password = ['bbbccc','aaabbb','cccddd']
bad_password  = ['table','desktop','message','password','robot']

rbuffer = ''

class SpammerScoringScript(BaseScoringScript):
    
    def readline(self,s):
        global rbuffer
        if '\n' in rbuffer:
            pos = rbuffer.find('\n')
            result = rbuffer[:pos]
            rbuffer = rbuffer[pos+1:]
            return result
        
        data = rbuffer+s.recv(100)
        while ('\n' in data) == False:
            data += s.recv(100)
        pos = data.find('\n');
        rbuffer = data[pos+1:]
        return data[:pos]
            
    
    def read_flag(self,s, username, password):
        s.send('login %s %s\n'%(username,password))
        res = self.readline(s)
        #print "Login %r"%res
    
        if res[:3] != "200":
            return ""
    
        s.send('stat\n')
        res = self.readline(s)
        #print "Stat %r"%res
        if res[:5] == "There":
            return ""
        
        res = self.readline(s)
        flag = res[4:]
        
        while res[:3] != "200":
            res = self.readline(s)
        
        return flag
        
        
    def create_flag(self,s, flag):
        username = self.getRandomString(6)
        password = random.choice(good_password)
        s.send('new %s %s\n'%(username,password))
        
        res = self.readline(s)
        #print "RES1: %r"%res
        
        if res[:3] != "200":
            return ""
        
        s.send("to: xxxx\n")
        res = self.readline(s)
        #print "TO: %r"%res
        
        s.send("spam\n")
        res = self.readline(s)
        res = self.readline(s)
        res = self.readline(s)
        #print "SPAM: %r"%res
        
        s.send("%s\n"%flag)
        s.send(".\n")
        res = self.readline(s)
        #print "END: %r"%res
        
        return username+":"+password
    
    def doScoring(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.teamIp, 4570))
            
            res = self.readline(s)
            res = self.readline(s)
            res = self.readline(s)
            
            
            if self.cookie != None:
                username, password = self.cookie.split(":")
                oldFlag = self.read_flag(s,username,password)
                self.validatePreviousFlag(oldFlag)
            
            self.cookie = self.create_flag(s,self.getNewFlagText())
            
            s.send("exit\n")
            s.close()
            
            self.returnVal.setSuccess()
            
        except Exception, e:
            self.output.write("ERROR: %s" % (e))
            self.returnVal.setError()

    def exerciseService(self):
        pass
    
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return SpammerScoringScript