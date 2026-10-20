#! /usr/bin/python
import cgi, sys, fcntl

def luhn_checksum(card_number):
    def digits_of(n):
    	digit_list = list()
    	for d in str(n):
    		try:
    			v = int(d)
    		except:
    			v = 0
    		digit_list.append(0) 
        return digit_list
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10


def is_luhn_valid(card_number):
    return luhn_checksum(card_number) == 0
   

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
			if l[1] == cc:
				entry = (l[0], l[2], ' '.join(l[4:]))
				res.append(entry)
	except Exception, e:
		print "<p>Sorry. Due to a server error (1) we are not able to process your request: %s.</p></body></html>" % str(e)
		if f != None: 
			f.close()
		sys.exit()
	return res


def create_file(data, cc):
	cc = cc.replace('/', 'X')
   	out = open("../reports/%s" % cc, 'w+')
	out.write('<html>\n <head>\n  <title>Donation Summary</title>\n </head>\n <body bgcolor="#6699ff" textcolor=white>\n')
	try:
		for l in data:
			out.write("  <p>%s: %s: %s</p>\n"%(l[0],l[1],l[2]))
	except Exception, e:
		print "<p>Sorry. Due to a server error (3) we are not able to process your request: %s.</p></body></html>" % str(e)
		if out != None: 
			out.close()
		sys.exit()
	out.write(' </body>\n</html>\n')
	out.close()
	return
	
				
def add(filename, cc, candidate, value, comment):
	f = None
	try:
		f = open(filename, 'a')
		fcntl.flock(f, fcntl.LOCK_EX)
		f.write("%s %s %d -- %s \r\n" % (candidate, cc, value, comment))
		fcntl.flock(f, fcntl.LOCK_UN)
		f.close()
	except:
		if f != None:
			f.close()
	return


print "Content-Type: text/html\n"
print
print '<html>\n  <head>\n  </head>\n  <body bgcolor="#6699ff" textcolor=white>'

form = cgi.FieldStorage()
candidate = form["candidate"].value
ccard = form["cc"].value
s_amount = form["amount"].value
if form.has_key("comment"):
	comment = form["comment"].value
else:
	comment = "none"
filename = "donations.bin"
amount = 0

try:
	amount = int(s_amount)
except:
	print "<h1>Value Error!!</h1><p>The donation must be an integer number.</p>"
	print "</body></html>"
	sys.exit()

if len(ccard) != 16:
	print "<h1>Credit Card Error</h1><p>Please use a complete credit card number.</p>"
	print "</body></html>"
	sys.exit()

if not is_luhn_valid(ccard):
	print "<h1>Credit Card Error</h1><p>Please use a valid credit card number.</p>"
	print "</body></html>"
	sys.exit()

add(filename, ccard, candidate, amount, comment)

data = load(filename, ccard)
create_file(data, ccard)
                                                                                                   
print "<b>Thank you very much for your donation!</b>"
linkname = ccard.replace('/','X')
print '<p>Click <a href="../reports/%s">here</a> to review your donations.</p>' % linkname
print '</body></html>'
