import sys

#sys.path.append("./ctf_bank")

import scoringScript
import traceback
import random
import string
import pybrowse
import browserpersonality

class IpalScoringScript( scoringScript.BaseScoringScript ):

	def doScoring( self ):
		personality = browserpersonality.getRandomPersonality()
		browser = pybrowse.Browser("http://" + self.teamIp + ":3000/", personality, False)
		browser.doRedirects()
		browser = browser.click("/welcome")
		browser.parse()

		browser = browser.click("/session/signup")
		browser.parse()

		form = browser.forms[0]
		name = ''.join( [random.choice( string.ascii_letters ) for x in range( 0, 8 )] )
		pwd = ''.join( [random.choice( string.ascii_letters ) for x in range( 0, 8 )] )
		form.fields["user[login]"] = name
		form.fields["user[email]"]  = name
		form.fields["user[password]"]  = pwd
		form.fields["user[password_confirmation]"]  = pwd
		form.fields["user[image_link]"] = "thumb_%d.jpg" % random.randint(1, 11)
		form.fields["user[description]"] = name

		browser = form.click("/session/signup")
		browser.parse()
		browser = browser.click("/welcome")
		
		if(browser.page.find("Logout")==-1):
			self.returnVal.setCreateAcctFailed( )
			self.output.write("Unable to create account\n")
			return


		browser = browser.click("/user/show")
		browser.parse()

		browser = browser.click("/user/show_deposits")
		browser.parse()

		browser = browser.click("/deposit/new")
		browser.parse()

		form = browser.forms[0]
		form.fields["check_id"] = self.check
		form.fields["currency_id"] = random.randint(1, 10)
		browser = form.click("/deposit/create")
		browser.parse()

		browser = browser.click("/user/show_deposits")
		browser.parse()
		
		pos = browser.page.find("Deposit was successfully created.")
		if pos < 0:
			self.returnVal.setDepositFailed()
			self.output.write("Error, cannot deposit a check\n")
			return


		start = browser.page.find("withdraw/",pos);
		start = start + 9
		end = browser.page.find("\"", start) 
		
		#print browser.page
		#print "Account =",browser.page[pos:end]
		pnum = browser.page[start:end]
		#print "A",pnum
		#print name

		print pnum
		browser = browser.click("/deposit/withdraw/%s" % pnum)
		browser.parse()
		browser.printInfo()
		
		form = browser.forms[0]
		form.fields["id"] = pnum
		form.fields["iban"] = self.iban
		browser = form.click("/deposit/destroy")
		browser.parse()

		browser = browser.click("/user/show_deposits")
		browser.parse()
		
		if(browser.page.find("No deposit yet!")==-1):
			self.returnVal.setFunctionalityFailed()
			self.output.write("Error, withdraw a check\n")
			return

		browser = browser.click("/session/logout")
		browser.parse()

		if (browser.page.find("Login")>0):
			self.returnVal.setSuccess()
			return

		self.returnVal.setTransferFailed()

	def exerciseService( self ):
		pass	

def getScoringScript( ):
    return IpalScoringScript






