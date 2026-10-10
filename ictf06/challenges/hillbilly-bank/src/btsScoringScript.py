import scoringScript
import threading
import time
import random
import string
import traceback
import sys
import socket
sys.path.append("./pybrowse")
import pybrowse
import browserpersonality

def generateServiceAccount( ):
    return ''.join( [random.choice( string.ascii_letters ) for x in range( 0, 10 )] )

class SampleScoringScript( scoringScript.BaseScoringScript ):
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

        personality = browserpersonality.getRandomPersonality()
        browser = pybrowse.Browser("http://" + self.teamIp + ":481516", personality, False)
        browser.doRedirects()
        browser = browser.click("/subscribe")
        browser.parse()
        
        form = browser.forms[0]
        username = ''.join( [random.choice( string.ascii_letters ) for x in range( 0, 8 )] )
        lastname = ''.join( [random.choice( string.ascii_letters ) for x in range( 0, 8 )] )
        password = ''.join( [random.choice( string.ascii_letters ) for x in range( 0, 8 )] )
        domain = ''.join( [random.choice( string.ascii_letters ) for x in range( 0, 8 )] )

        self.cookie = username + ":" + password

        form.fields["salutation"] = random.choice(["Mr", "Mrs", "Dr", "Prof"])
        form.fields["firstname"]  = username
        form.fields["lastname"]  = lastname
        form.fields["email"]  = username + "@" + domain + "." + random.choice(["com", "edu", "org"])
        form.fields["echeck"]  = self.check
        form.fields["username"]  = username
        form.fields["password"]  = password
        form.fields["question"]  = random.choice(['Favorite', 'Best', 'Worst']) + " " + random.choice(['color', 'animal', 'food'])
        form.fields["answer"]  = random.choice(['Pizza', 'Dog', 'Hot dog'])

        browser = form.click(None)
        browser.parse()

        if browser.page.find("Congratulations") ==  -1:
            self.retVal.setCreateAcctFailed()
            return

        browser = browser.click('/login')
        browser.parse()

        browser=browser.click("authenticate?username=" + username + "&password=" + password)

#        form = browser.forms[0]
#        form.fields["username"] = username
#        form.fields["password"] = password
#        browser = form.click(None)
        browser.parse()

        print browser.page
        if browser.page.find("Congratulations") ==  -1:
            self.output.write("Login failed")
            self.retVal.setCreateAcctFailed()
            return

        browser=browser.click("transfer?amount=" + str(self.transferAmount) + "&iban=" + self.iban)

#        form = browser.forms[0]
#        form.fields["amount"] = self.transferAmount
#        form.fields["iban"] = self.iban
#        browser = form.click(None)
        browser.parse()

        print browser.page
        if browser.page.find("Congratulations") ==  -1:
            self.output.write("Login failed")
            self.retVal.setTransferFailed()
            return

        try:
            self.exerciseService()
        except Exception, e:
            self.returnVal.setFunctionalityFailed()
            print e
            return

        self.returnVal.setSuccess()
        return
    
    def exerciseService( self ):
        """
        make use of your service in some psuedo random fashion, but don't do any actual transfers. this function will
        just be called every once in awhile in order to create some background noise.
        """
        print "%s called..." % ( __name__ + '.exerciseService' )
        
        print "self.cookie == <%s>, if this is not None then we can use it here to log into a previous account." % ( self.cookie )
        
#        personality = browserpersonality.getRandomPersonality()
#        browser = pybrowse.Browser("http://" + self.teamIp + ":481516", personality, False)
#        browser.doRedirects()
#        browser = browser.click(random.choice(["subscribe", ";ogin", "terms", "support", "logout"]))
#        browser.parse()
#        index = random.randint(0, len(browser.links) - 1)
#        link = browser.links[index]
#        browser.click(link)
        
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
