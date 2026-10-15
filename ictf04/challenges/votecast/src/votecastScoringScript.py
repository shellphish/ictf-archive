import socket
import random
import string
from ImageScripts.BaseScoringScript import BaseScoringScript 

port = 1969

class VotecastScoringScript(BaseScoringScript):
     
    def sendMessage(self, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.teamIp, port))
        sock.send(message)
        sock.shutdown(1)
            
        response = ""
        msg = ""
        while(True):
            msg = sock.recv(1024)
            if(not msg):
                break
            response += msg
        
        sock.close()
        return response
        
    
    def encrypt(self, msg):
        key = 'F2654hD4'
        encrypted_message = ""
        for i in range(0,len(msg)):
            encrypted_message += "%02X" % (ord(key[i%len(key)])^ord(msg[i]))
        return encrypted_message
        
    def decrypt(self, msg):
        key = 'F2654hD4'
        count = 0
        decrypted_message = ""
        for i in range(0,len(msg),2):
            decrypted_message +=  chr(int(msg[i]+msg[i+1],16) ^ ord(key[count%len(key)]))
            count += 1
        return decrypted_message
            
    def doScoring(self):
        
        #get old flag
        if self.cookie != None:
            try:
                wwid = self.cookie
                vote = self.getRandomString(random.randint(5,10))
        
                response = self.sendMessage(self.encrypt("!"+wwid+" "+vote))
                successPtr = response.find("OK")
                if successPtr != -1:
                    oldFlag = self.decrypt(response[successPtr+3:].strip())
                    self.validatePreviousFlag(oldFlag)
                else:
                    self.returnVal.setGetFlagFailed()
                
            except Exception, e:
                self.output.write("got exception %s getting flag" % (e))
                self.returnVal.setError()
        
        #set the new flag
        try:  
            wwid = self.getRandomString(random.randint(6,8))
            vote = self.getNewFlagText()
            
            response = self.sendMessage(self.encrypt("!"+wwid+" "+vote))
            
            successPtr = response.find("OK")
            if successPtr == -1:
                self.returnVal.setPostFlagFailed()
                return
            
            self.cookie = wwid
            self.returnVal.setSuccess()
            
        except Exception, e:
            self.returnVal.setError()
            self.output.write("got exception %s setting new flag" % (e))
            
    def exerciseService(self):
        pass
    
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return VotecastScoringScript