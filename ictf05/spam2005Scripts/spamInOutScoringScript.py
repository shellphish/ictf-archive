import sys
import socket
import string
import random

from ImageScripts.BaseScoringScript import BaseScoringScript 

spaminPort = 8008
spamoutPort = 8009

randAlphabet = string.ascii_letters + string.digits

headerString = "SPAM-IN-SPAM-OUT"

class SpamInOutScoringScript(BaseScoringScript):

    def doScoring(self):  
        #get flag is spamout
        if self.cookie != None:
            try:
                s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                s.connect(( self.teamIp, spamoutPort ))
                s.sendall(headerString + "\n" + self.cookie + "\n")
                
                recvString = ""
                while True:
                    data = s.recv(1)
                    if not data:
                        break
                    recvString += data
                    
                #print recvString
                oldFlag = recvString
                self.validatePreviousFlag(oldFlag)
                
                s.close( )
            except Exception, e:
                self.returnVal.setGetFlagFailed()
                self.output.write("got exception trying to read old flag: %s" % (e))
       
        #set flag is spamin
        try:
            s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            s.connect( ( self.teamIp, spaminPort ) )
            newName = "".join( [ random.choice( randAlphabet ) for i in range( 0, random.randrange( 6, 24 ) ) ] )
            
            s.sendall( headerString + "\n" + newName + "\n" + self.getNewFlagText() + "\n" )

            recvString = ""
            while True:
                data = s.recv( 1 )
                if not data:
                    break
                recvString += data
    
            self.cookie = newName
            s.close()
            
            self.returnVal.setSuccess()
        
        except Exception, e:
            self.output.write("got exception trying to set new flag: %s" % (e))
            self.returnVal.setPostFlagFailed()
        
    def exerciseService(self):
        if self.cookie != None:
            try:
                s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                s.connect(( self.teamIp, spamoutPort ))
                s.sendall(headerString + "\n" + self.cookie + "\n")
            except:
                pass
        
def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    return SpamInOutScoringScript