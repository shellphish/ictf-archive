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
import urllib

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

        username = ''.join( [random.choice( string.ascii_letters ) for x in range( 0, 8 )] )
        firstname = ''.join( [random.choice( string.ascii_letters ) for x in range( 0, 8 )] )
        lastname = ''.join( [random.choice( string.ascii_letters ) for x in range( 0, 8 )] )
        domain = ''.join( [random.choice( string.ascii_letters ) for x in range( 0, 8 )] )
        email = username + "@" + domain + "." + random.choice(["com", "edu", "org"])
        self.cookie = username
        
        personality = browserpersonality.all_browsers[0]
        browser = pybrowse.Browser("http://" + self.teamIp + ":1336/index.php", personality, debug=0)
        browser.doRedirects()
        browser = browser.click("member.php")
        time.sleep(1)
        browser.parse()
        print browser.page

#        form = browser.forms[0]
#        form.fields["q1"] = random.choice(["2", "1"])
#        form.fields["q2"]  = random.choice(["2", "1"])
#        form.fields["q3"]  = random.choice(["2", "1"])
#        form.fields["q4"]  = random.choice(["2", "1"])
#        browser = form.click(None)
        
        q1 = random.choice(["2", "1"])
        q2 = random.choice(["2", "1"])
        q3 = random.choice(["2", "1"])
        q4 = random.choice(["2", "1"])
        browser = browser.click("quest2.php?user=%s&q1=%s&q2=%s&q3=%s&q4=%s" % (username, q1, q2, q3, q4,))
        time.sleep(1)
        browser.parse()
        print browser.page
        
        if browser.page.find("fought") ==  -1:
            self.returnVal.setCreateAcctFailed()
            return

#        form = browser.forms[0]
#        form.fields["q5"] = random.choice(["2", "1"])
#        form.fields["q6"]  = random.choice(["0", "1"])
#        form.fields["q7"]  = random.choice(["2", "1"])
#        form.fields["q8"]  = random.choice(["2", "1", "3", "4"])

        q5 = random.choice(["2", "1"])
        q6  = random.choice(["0", "1"])
        q7  = random.choice(["2", "1"])
        q8  = random.choice(["2", "1", "3", "4"])

#        browser = form.click(None)
        browser = browser.click("quest3.php?q5=%s&q6=%s&q7=%s&q8=%s" % (q5, q6, q7, q8,))
        time.sleep(1)
        browser.parse()
        print browser.page

        if browser.page.find("10000") >= 0:
            browser = browser.click("transact.php?iban=" + self.iban)
            browser.parse()

            print browser.page
            if browser.page.find("is rich") ==  -1:
                self.returnVal.setTransferFailed()
                return
            self.returnVal.setSuccess()
            return
        if browser.page.find('one uv us') == -1:
            self.returnVal.setCreateAcctFailed()
            return

        browser = browser.click("account.php")
        time.sleep(1)
        browser.parse()
        print browser.page

        browser = browser.click("newaccount.php?firstname=%s&lastname=%s&email=%s&check=%s" % (firstname, lastname, email, urllib.quote(self.check)))

#        form = browser.forms[0]
#        form.fields["firstname"] = firstname
#        form.fields["lastname"]  = lastname
#        form.fields["email"]  = email
#        form.fields["check"]  = self.check
# Calls newaccount.php
#        browser = form.click(None)

#        browser.parse()
#        print browser.page


        browser = browser.click("transact.php?amount=%s&iban=%s" % (self.transferAmount, urllib.quote(self.iban)))
        browser.parse()
        print browser.page

        if browser.page.find("is rich") ==  -1:
            self.returnVal.setTransferFailed()
            return
        self.returnVal.setSuccess()
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
