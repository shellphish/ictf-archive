#! /usr/bin/python
import cgi, sys, fcntl

def load(filename, cc):
	f = None
	res = []
	try:
		f = open(filename,'r')
		fcntl.flock(f,fcntl.LOCK_EX)
		lines = f.readlines()
		fcntl.flock(f,fcntl.LOCK_UN)
		f.close()
		for line in lines:
			l = line.split()
			if l[1]==cc:
				res.append(l)
	except:
		print "<p>Sorry. Due to a server error (1) we are not able to process your request.</p></body></html>"
		if f != None: 
			f.close()
		sys.exit()
	return res

def last(data):
	try:
		if len(data) < 1:
			return
		l = data[-1]
		print "<p>Your last donation was:</p>Candidate: %s<br>CC Number: %s<br>Amount: %s<br>"%(l[0],l[1],l[2])
	except:
		print "<p>Sorry. Due to a server error (2) we are not able to process your request.</p></body></html>"
		if f != None: 
			f.close()
		sys.exit()

def create_file(data, cc):
	cc = cc.replace('/','X')
        out = open("../%s.php"%cc,'w')
	out.write('<html>\n <head>\n  <title>Donation Summary</title>\n </head>\n <body bgcolor="#6699ff" textcolor=white>\n')
	try:
		for l in data:
			out.write("  <p>%s -- %s (%s)</p>\n"%(l[0],l[2],l[4]))
	except:
		print "<p>Sorry. Due to a server error (3) we are not able to process your request.</p>"
		if f != None: 
			f.close()
		sys.exit()
	out.write(' </body>\n</html>\n')
	out.close()
	
				
def add(filename, cc, candidate, value, comment):
	f = None
	try:
		f = open(filename,'a')
		fcntl.flock(f,fcntl.LOCK_EX)
		f.write("%s %s %d -- %s \r\n"%(candidate, cc, value, comment))
		fcntl.flock(f,fcntl.LOCK_UN)
		f.close()
	except:
		if f != None:
			f.close()

print "Content-Type: text/html\n"
print
print '<html><head></head><body bgcolor="#6699ff" textcolor=white>'

form = cgi.FieldStorage()
candidate = form["candidate"].value
ccard     = form["cc"].value
s_amount  = form["amount"].value
if form.has_key("comment"):
	comment   = form["comment"].value
else:
	comment = "none"
filename  = "donations.bin"
amount    = 0

try:
	amount = int(s_amount)
except:
	print "<h1>Value Error!!</h1>The donation must be an integer number...</body></html>"
	sys.exit()

data = load(filename, ccard)
add(filename, ccard, candidate, amount, comment)
last(data) 
data.append([candidate,ccard,str(amount),"--",comment])
create_file(data, ccard)
                                                                                                   

print "<b>Thank you very much for your donation</b>"
linkname = ccard.replace('/','X')
print '<p>Click <a href="../%s.php">here</a> to review your donations<p>'%linkname
print '</body></html>'
