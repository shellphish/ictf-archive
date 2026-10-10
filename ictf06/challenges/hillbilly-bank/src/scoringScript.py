import StringIO
import os
import centralbank

class ThreadReturnVal:
    
    SUCCESS               = 0
    DEPOSIT_FAILED        = 1
    TRANSFER_FAILED       = 2
    CONNECT_FAILED        = 3
    CREATE_ACCT_FAILURE   = 4
    FUNCTIONALITY_FAILED  = 5
    ERROR                 = 6
    
    def __init__( self ):
        self.exitStatus = None                  #set to one of the constants defined above
        self.retVal     = StringIO.StringIO( )  #should be a string describing the failure if necessary
    
    def __str__( self ):
        aStr = StringIO.StringIO( )
        aStr.write( "<exitStatus:" )
        if self.exitStatus == None:
            aStr.write( "None" )
        elif self.exitStatus == ThreadReturnVal.SUCCESS:
            aStr.write( "SUCCESS" )
        elif self.exitStatus == ThreadReturnVal.DEPOSIT_FAILED:
            aStr.write( "DEPOSIT_FAILED" )
        elif self.exitStatus == ThreadReturnVal.TRANSFER_FAILED:
            aStr.write( "TRANSFER_FAILED" )
        elif self.exitStatus == ThreadReturnVal.CONNECT_FAILED:
            aStr.write( "CONNECT_FAILED" )
        elif self.exitStatus == ThreadReturnVal.CREATE_ACCT_FAILURE:
            aStr.write( "CREATE_ACCT_FAILED" )
        elif self.exitStatus == ThreadReturnVal.FUNCTIONALITY_FAILED:
            aStr.write( "FUNCTIONALITY_FAILED" )
        elif self.exitStatus == ThreadReturnVal.ERROR:
            aStr.write( "ERROR" )
        aStr.write( "|retVal:" + self.retVal.getvalue( ) + ">" )
        
        return aStr.getvalue( )
    
    def setConnectFailed( self ):
        self.exitStatus = ThreadReturnVal.CONNECT_FAILED
    
    def setCreateAcctFailed( self ):
        self.exitStatus = ThreadReturnVal.CREATE_ACCT_FAILURE
    
    def setDepositFailed( self ):
        self.exitStatus = ThreadReturnVal.DEPOSIT_FAILED
    
    def setTransferFailed( self ):
        self.exitStatus = ThreadReturnVal.TRANSFER_FAILED
    
    def setFunctionalityFailed( self ):
        self.exitStatus = ThreadReturnVal.FUNCTIONALITY_FAILED
    
    def setSuccess( self ):
        self.exitStatus = ThreadReturnVal.SUCCESS
    
    def setError( self ):
        self.exitStatus = ThreadReturnVal.ERROR

class BaseScoringScript:
    DO_SCORE         = 'doScoring'
    EXERCISE_SERVICE = 'exerciseService'
    
    def __init__( self, roundEnd, teamIp, depositAmount=None, transferAmount=None, check=None, iban=None, cookie=None, action='doScoring' ):
        self.returnVal      = ThreadReturnVal( )    #call any of the ThreadReturnVal.set*( ) methods to communicate the
                                                    #outcome of session
        self.teamIp         = teamIp                #the team ip
        self.depositAmount  = depositAmount         #the amount present within the check
        self.transferAmount = transferAmount        #the amount present within the iban
        self.check          = check                 #the check to deposit with
        self.iban           = iban                  #the scorbot iban, with the transfer amount embedded
        self.roundEnd       = roundEnd              #the time as returned by time.time( ) at which the round will end
                                                    #this should be used to set a timer ( threading.Timer( ) ) that
                                                    #cleans up (kills) any subprocesses spawned by your script
        self.output         = self.returnVal.retVal #use this the same as a file to write out messages concerning script
                                                    #progress that could be useful for debugging or reasons for service
                                                    #failure etc...
        self.action         = action                #used to indicate what action the script should perform
        self.cookie         = cookie                #can be used in exercise service to log into a previous account, etc...
                                                    #this is just a way for a service script to save some sort of state
                                                    #in order to save a cookie, just save it in self.cookie. the next time
                                                    #this script is executed self.cookie will contain what was previously
                                                    #saved there. if you want to reuse the same cookie again, don't change
                                                    #it and it will be passed back on the next invocation. the first round
                                                    #this value will be None
    
    def __call__( self ):
        try:
            getattr( self, self.action )( )
        except AttributeError, e:
            self.output.write( "error dispatching action: %s" % ( str( e ) ) )
    
    def doScoring( self ):
        print "override me!\ngot:\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s" % ( self.teamIp, 
                                                                           str( self.depositAmount ), 
                                                                           str( self.transferAmount ), 
                                                                           self.check, 
                                                                           self.iban, 
                                                                           self.cookie, 
                                                                           str( self.roundEnd ), 
                                                                           self.returnVal, 
                                                                           self.action )
    
    def exerciseService( self ):
        """
        this should just run through the different functionality for your service.
        """
        print "override me!\ngot:\n%s\n%s\n%s\n%s\n%s" % ( self.teamIp, str( self.roundEnd ), self.cookie, self.returnVal, self.action )

def getScoringScript( ):
    """
    this function should be defined in each scoring module so that the bot can easily
    instantiate the appropriate class.
    """
    return BaseScoringScript
