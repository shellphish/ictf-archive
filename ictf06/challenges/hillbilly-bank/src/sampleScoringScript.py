import scoringScript
import threading
import time
import random
import string
import traceback
import sys
import socket

def generateServiceAccount( ):
    return ''.join( [random.choice( string.ascii_letters ) for x in range( 0, 10 )] )

class TestTimeoutScript( scoringScript.BaseScoringScript ):
    TIMEOUT = 60
    
    def doScoring( self ):
        self.output.write( "starting %s at %s" % ( __name__, time.strftime( "%H:%M:%S", time.localtime( ) ) ) )
        time.sleep( TestTimeoutScript.TIMEOUT )
        self.output.write( "stopping %s at %s" % ( __name__, time.strftime( "%H:%M:%S", time.localtime( ) ) ) )

class TestFinishScript( scoringScript.BaseScoringScript ):
    TIMEOUT = 10
    
    def doScoring( self ):
        self.output.write( "starting %s at %s" % ( __name__, time.strftime( "%H:%M:%S", time.localtime( ) ) ) )
        time.sleep( TestFinishScript.TIMEOUT )
        self.output.write( "stopping %s at %s" % ( __name__, time.strftime( "%H:%M:%S", time.localtime( ) ) ) )
        

class TestRandomScript( scoringScript.BaseScoringScript ):
    TIMEOUT_MIN = 10
    TIMEOUT_MAX = 30
    
    def doScoring( self ):
        sleepTime = random.randint( TestRandomScript.TIMEOUT_MIN, TestRandomScript.TIMEOUT_MAX )
        self.output.write( "starting %s at %s, sleeping for %i" % ( __name__, time.strftime( "%H:%M:%S", time.localtime( ) ), sleepTime ) )
        time.sleep( sleepTime )
        self.output.write( "stopping %s at %s" % ( __name__, time.strftime( "%H:%M:%S", time.localtime( ) ) ) )
        self.returnVal.setSuccess( )
        self.cookie = generateServiceAccount( )
        #self.cookie = "reloaded!!!!"

class SampleScoringScript( scoringScript.BaseScoringScript ):
    def connectToService( self ):
        """
        use pybrowse, pexpect, etc...
        """
        return True
    
    def createNewAcct( self ):
        """
        do whatever is necessary to create an account with your service. maybe return a cookie
        here so that next time the script is called it can log back into this account.
        """
        return "bob:%s" % ( generateServiceAccount( ) )
    
    def depositCheck( self, aCheck ):
        """
        deposit a check into your account.
        """
        return True
    
    def transferMoney( self ):
        """
        use self.iban
        """
        return True
    
    def killProcesses( self ):
        """
        set a timer to call this function and send all processes that have been spawned the kill signal.
        """
        pass
    
    def doScoring( self ):
        """
        this is the entry point for the scoring script.
        """
        print "self.teamIp: %s" % ( self.teamIp )
        print "self.depositAmount: %i" % ( self.depositAmount )
        print "self.transferAmount: %i" % ( self.transferAmount )
        print "self.check: %s" % ( self.check )
        print "self.iban: %s" % ( self.iban )
        print "self.roundEnd: %d" % ( self.roundEnd )
        print "self.returnVal: %s"  % ( str( self.returnVal ) )
        print "self.cookie: %s" % ( self.cookie )
        print "self.action: %s" % ( self.action )

        self.cookie = generateServiceAccount()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto("N " + self.cookie, (self.teamIp, 2342))
        (data, address) = s.recvfrom(65536)
        print data
        (code, msg) = data.split("\r\n")
        if code != "311":
            self.returnVal.setCreateAcctFailed()
            return
        
        try:
            self.exerciseService()
        except Exception, e:
            self.returnVal.setFunctionalityFailed()
            print e
            return

        s.sendto("D " + self.cookie + " " + self.check, (self.teamIp, 2342))
        (data, address) = s.recvfrom(65536)
        (code, msg) = data.split("\r\n")
        if code != "382":
            self.returnVal.setDepositFailed()
            return

        s.sendto("T " + self.cookie + " " + self.iban + " " + str(self.transferAmount), (self.teamIp, 2342))
        (data, address) = s.recvfrom(65536)
        (code, msg) = data.split("\r\n")
        if code != "711":
            self.returnVal.setTransferFailed()
            return

        """
        if you absolutely must spawn some process (this includes pexpect), set a timer to call a function that will kill that process in the event
        that it hangs. for example:
        
        timer = threading.Timer( self.roundEnd - time.time( ), self.killProcesses )
        timer.start( )
        
        """
        self.returnVal.setSuccess()
        return
    
    def exerciseService( self ):
        """
        make use of your service in some psuedo random fashion, but don't do any actual transfers. this function will
        just be called every once in awhile in order to create some background noise.
        """
        print "%s called..." % ( __name__ + '.exerciseService' )
        
        print "self.cookie == <%s>, if this is not None then we can use it here to log into a previous account." % ( self.cookie )
        
        self.returnVal.setSuccess( )
        
        return True
        

def getScoringScript( ):
    """
    this must be defined in every scoring module.
    """
    
    #x = [TestTimeoutScript, TestFinishScript, TestRandomScript]
    
    #return random.choice( x )
    #return TestRandomScript
    return SampleScoringScript
