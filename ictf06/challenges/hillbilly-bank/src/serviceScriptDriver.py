import socket
import os
import sys
import threading
import types
import time

import centralbank

pemFile        = "ctf_bank/keys/private.pem"

def loadModule( modName ):
    dynModule = __import__( modName, globals( ), locals( ), ['getScoringScript'] )
    return dynModule

def printUsage( exitVal=0 ):
    print \
"""
usage: %s [options]
    
    options:
        -a <action>             - action can be S or E, S is the default and calls doScoring, E calls exerciseService
        -i <ip addr>            - ip addr to pass to your script
        -m <module.name>        - the module name that your script resides in as you would write it in an import statement
        -d <deposit amount>     - the deposit amount (check amount)
        -t <transfer amount>    - the transfer amount (iban amount)
        -T <script timeout>     - the amount of time to wait before joining with your script (integer value)
        -c <cookie>             - whatever you want to pass to your script as a cookie
        -I <team id>            - the team id
        -r <round number>       - the round number
        (-h|--help)             - print this help and exit
    
    notes:
        -the only really required options are -i and -m...
        -change the global variable pemFile to point to a private key somewhere on your machine.
        
""" % ( sys.argv[0] )
    sys.exit( exitVal )

def main( ):
    ip             = '10.0.0.1'
    module         = 'change.Me'
    action         = 'doScoring'
    depositAmount  = 1000
    transferAmount = 500
    scriptTimeout  = 20
    cookie         = ""
    teamId         = 1
    roundNumber    = 1
    
    if '-h' in sys.argv or '--help' in sys.argv:
        printUsage( )
    
    skip = 0
    try:    
        for i in range( 1, len( sys.argv ) ):
            if skip:
                skip = skip - 1
                continue
            if sys.argv[i] == '-a':
                skip = 1
                if sys.argv[i+1] == 'S':
                    action = 'doScoring'
                elif sys.argv[i+1] == 'E':
                    action = 'exerciseService'
                else:
                    printUsage( 1 ) 
            elif sys.argv[i] == '-i':
                skip = 1
                ip = sys.argv[i+1]
            elif sys.argv[i] == '-m':
                skip = 1
                module = sys.argv[i+1]
            elif sys.argv[i] == '-d':
                skip = 1
                depositAmount = int( sys.argv[i+1] )
            elif sys.argv[i] == '-t':
                skip = 1
                transferAmount = int( sys.argv[i+1] )
            elif sys.argv[i] == '-T':
                skip = 1
                scriptTimeout = int( sys.argv[i+1] )
            elif sys.argv[i] == '-c':
                skip = 1
                cookie = sys.argv[i+1]
            elif sys.argv[i] == '-I':
                skip = 1
                teamId = int( sys.argv[i+1] )
            elif sys.argv[i] == '-r':
                skip = 1
                roundNumber = int( sys.argv[i+1] )
            else:
                printUsage( 1 )
    except IndexError:
        printUsage( 1 )
    except ValueError:
        printUsage( 1 )

    print\
"""
------------------------------------------------------------------
ip              %s
module          %s
action          %s
depositAmount   %i
transferAmount  %i
scriptTimeout   %i
cookie          %s
teamId          %i
roundNumber     %i
------------------------------------------------------------------
""" % ( ip, module, action, depositAmount, transferAmount, scriptTimeout, cookie, teamId, roundNumber )
    
    print "loading %s..." % ( module )
    
    try:
        module = loadModule( module )
    except Exception, e:
        #traceback.print_exc( )
        print "couldn't load %s, make sure it is in your PYTHONPATH: %s" % ( module, str( e ) )
        return -1
    
    print "getting scoring class..."
    
    getScoringScript = None
    try:
        #print dir( module )
        getScoringScript = getattr( module, 'getScoringScript' )
        assert( type( getScoringScript ) == types.FunctionType )
    except AttributeError, e:
        print "the scoring module must define a function named 'getScoringScript' that returns the scoring class: <%s>" % ( str( e ) )
        return -1
    except AssertionError, e:
        print "the scoring module must define a *function* named 'getScoringScript' that returns the scoring class: <%s>" % ( str( e ) )
        return -1
    
    scoringScript = getScoringScript( )
    
    if not os.path.isfile( pemFile ):
        print "<%s> is not a regular file, please substitute a valid pem file for the 'pemFile' global variable" % ( pemFile )
        return -1
    
    theBank = centralbank.Bank( pemFile )
    
    iban  = theBank.createScorebotIBAN( teamId, roundNumber, transferAmount )
    check = theBank.makeCheck( teamId, depositAmount )
    
    print "instantiating %s..." % ( scoringScript.__name__ )
    
    scoringScriptInstance = scoringScript( time.time( ) + scriptTimeout,
                                           ip,
                                           depositAmount,
                                           transferAmount,
                                           check,
                                           iban, 
                                           cookie, 
                                           action )
    
    scoringThread = threading.Thread( target=scoringScriptInstance )
    scoringThread.setDaemon( True )
    
    print "starting scoring thread...\n"
    
    scoringThread.start( )
    
    time.sleep( scriptTimeout )
    
    if scoringThread.isAlive( ):
        print "\nyour script timed out!"
        scoringScriptInstance.output.flush( )
    else:
        print "\nscript exited... joining."
        scoringThread.join( )

    print "scoring script exited with: %s" % ( str( scoringScriptInstance.returnVal ) )
    
    return 0

if __name__ == "__main__":
    sys.exit( main( ) )
