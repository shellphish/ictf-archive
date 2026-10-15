import socket
import random

from ImageScripts.BaseScoringScript import BaseScoringScript 
from ImageScripts.Utility import pybrowse, browserpersonality

port = 7413
class DiscussitScoringScript(BaseScoringScript):
     
    def initConversation(self, message, sock):
        sock.send(message)
        response = ""
        msg = ""
        while(True):
            response += sock.recv(1024)
            if(response.find("else!") != -1):
                break
            
        return response
    
    def askRandomQuestion(self,sock):
        start = ["How ","What ","Why ", "Where " , "When ", "Cows "]
        middle = ["is ", "are ", "were ", "was ", "come ", "over ", "long ", "Cows "]
        end = ["beer", "life", "Cows", "people", "the moon", "the game", "the weather", "binary"]
        
        filler = ["great ", "good ", "some ", "all ", "bad ", "tall ", "", "", "", ""]
        period = ["?\n","!\n",".\n"]
        
        msg = random.choice(start) + random.choice(middle) + random.choice(filler) + random.choice(end) + random.choice(period)
        sock.send(msg)
        return sock.recv(1024)
        
    def doScoring(self):
        #get old flag
        if self.cookie != None:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.teamIp, port))
                
                name = self.cookie
                topic = self.getRandomAlphaNum(random.randint(3,8))
                msg = name+" " + topic + "\n" 
                
                response = self.initConversation(msg,sock)
                successPtr = response.find("Last time")
                
                if successPtr != -1:
                    oldFlag = response[successPtr+32:][:self.getFlagSize()]
                    self.validatePreviousFlag(oldFlag)
                else:
                    self.returnVal.setGetFlagFailed()
                
                sock.close()
                
            except Exception, e:
                self.output.write("got exception %s getting flag" % (e))
                self.returnVal.setError()
    
        #set the new flag
        try:  
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.teamIp, port))
            
            name = self.getRandomString(random.randint(6,8))
            msg = name+" " + self.getNewFlagText() + "\n"    
            response = self.initConversation(msg,sock)
            
            successPtr = response.find("summoning operator")
            if successPtr == -1:
                self.returnVal.setPostFlagFailed()
                return
            
            for i in range(random.randint(1,3)):
                if len(self.askRandomQuestion(sock)) < 1:
                    self.returnVal.setFunctionalityFailed()
                    return
            
            sock.close()
            
            self.cookie = name
            self.returnVal.setSuccess()
            
           
        except Exception, e:
            self.returnVal.setError()
            self.output.write("got exception %s setting new flag" % (e))
            
    def exerciseService(self):
        try:  
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.teamIp, port))
            
            name = self.getRandomString(random.randint(6,8))
            topic = self.getRandomAlphaNum(random.randint(3,8))
            msg = name+" " + topic + "\n" 
            self.initConversation(msg,sock)
            
            for i in range(random.randint(1,3)):
                    self.askRandomQuestion(sock)
                    
            sock.close()
        except:
            pass
        
            
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return DiscussitScoringScript