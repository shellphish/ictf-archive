#! /usr/bin/python
import cgi
from string import *
from markov import *
from myhash import *

print "Content-Type: text/html\n"
print 

print "<html><body>"
print '<html><head><Title>Automatic Spam Generator</title><link href="/spam.css" rel="stylesheet" type="text/css"></head><body>'

#print '<html><head></head><body bgcolor="#6699ff" textcolor=white>'
#print '<form action="post"><input type="text" name="prova"></input> </form>'

print '</body></html>'


form = cgi.FieldStorage()


#print form
getvar=dict([(x, form[x].value) for x in form.keys() ])

#print getvar

try:

   if getvar["action"]=="generate":
	print '<a href="spamgen.py">Goto main page</a><br><a href="spamgen.py?action=generate">Generate again!</a>'
	print "<h1>Generated text</h1>"
	print '<p>'+mtext()+'</p>'

   elif getvar["action"]=="upload":
	print '<a href="spamgen.py">Goto main page</a>'
	print "<h1>Upload new text</h1>"

	print '<FORM ACTION="spamgen.py" METHOD="post" ENCTYPE="multipart/form-data">',

	print 'Username: <INPUT TYPE="text" NAME="uname">'
	print 'Password <INPUT type="password" name="pwd"><br>'

	print '<TEXTAREA name="thetext" rows="20" cols="80"></TEXTAREA>',

	print '<br><INPUT type="submit" value="Send"> <INPUT type="reset">'
	print '<br><INPUT type="hidden" name="action" value="upload"> '
	print '</FORM>'

	try:
		getvar["uname"] and getvar["pwd"] 
#		print "uname,pwd" , getvar["uname"],getvar["pwd"]

		f=open('user_db/'+hash(strip(getvar["uname"]+getvar["pwd"])),'a')
		f.write(getvar["thetext"]+'\n'+'-'*20+'END\n' );
		f.close()
		print '<p style="color:red"> Text updated successfully </p>'
	except: pass


   elif getvar["action"]=="read":
	print '<a href="spamgen.py">Goto main page</a>'
	print "<h1>Your uploaded text</h1>"

	print '<FORM ACTION="spamgen.py" METHOD="post"   ENCTYPE="multipart/form-data">',
#	print '<FORM ACTION="spamgen.py" METHOD="post"  >',
	print 'Username: <INPUT TYPE="text" NAME="uname">'
	print 'Password <INPUT TYPE="text" NAME="pwd"><br>'
	print '<br><INPUT type="submit" value="Send"> <INPUT type="reset">'
	print '<br><INPUT type="hidden" name="action" value="read"> '	
	print '</FORM>'
	try:
		getvar["uname"] and getvar["pwd"] 
#		print "uname,pwd" , getvar["uname"],getvar["pwd"], hash(strip(getvar["uname"]+getvar["pwd"]))
		f=open('user_db/'+hash(strip(getvar["uname"]+getvar["pwd"])),'r')
		print '<p>'
		start=1;
		k=0
		for l in f.readlines():
			if start: print '<h3 style="color:red">','Text number '+str(k),'</h3>';start=0; 
			if l.find('-'*20+'END') != -1 : start=1; k+=1;continue
			print l, '<br>'
		print '</p>'
		f.close()
	except: pass
except Exception, e:
#	print e	
#	print "got exception %s " % ( e )
	print "<h1>Automatic spam generator</h1>"
	print """

<p>Nowadays spam is a business!!! Don't get stuck in writing junk mails by hand, it consumes times and fantasy!
Use a random text generator instead, Here you are a service that generates random spam emails according to a 2-order markov model inferred from a knowledge database that you can increase.
</p>
<p>
To generate a new random junk mail just click <a href="spamgen.py?action=generate">here</a></li>'
</p>

<p>
You can also <a href="spamgen.py?action=upload">upload</a> new spam mail to increase the knowledge base giving a username e password. 
Eventually you can <a href="spamgen.py?action=read">browse all the junk mail you have uploaded</a> by providing the same username/pwd pair
</p>
"""	
	print '<ul><li><a href="spamgen.py?action=generate">Generate now!</a></li>'

	print '<li><a href="spamgen.py?action=upload">Increase the entropy!</a></li>'
	print '<li><a href="spamgen.py?action=read">See your stuff</a></li></ul>'

print '</body></html>'



