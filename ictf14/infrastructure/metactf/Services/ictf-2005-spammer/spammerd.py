#!/usr/bin/python

import SocketServer, os, time, sys, string, socket

banner = "SPAM Server\nVersion 4.5.3 (Testing)\n"

class Field:
    islist=0
    def __init__(self, name, default, fmt="H"):
        self.name = name
        if fmt[0] in "@=<>!":
            self.fmt = fmt
        else:
            self.fmt = "!"+fmt
        self.default = self.any2i(None,default)
        self.sz = struct.calcsize(self.fmt)

    def h2i(self, pkt, x):
        return x
    def i2h(self, pkt, x):
        return x
    def m2i(self, pkt, x):
        return x
    def i2m(self, pkt, x):
        if x is None:
            x = 0
        return x
    def any2i(self, pkt, x):
        return x
    def i2repr(self, pkt, x):
	if x is None:
	    x = 0
        return repr(self.i2h(pkt,x))
    def addfield(self, pkt, s, val):
        return s+struct.pack(self.fmt, self.i2m(pkt,val))
    def getfield(self, pkt, s):
        return  s[self.sz:], self.m2i(pkt, struct.unpack(self.fmt, s[:self.sz])[0])
    def copy(self, x):
        if hasattr(x, "copy"):
            return x.copy()
        elif type(x) is list:
            return x[:]
        else:
            return x
    def __eq__(self, other):
        return self.name == other
    def __hash__(self):
        return hash(self.name)
    def __repr__(self):
        return self.name

class StrField(Field):
    def i2m(self, pkt, x):
        if x is None:
            x = ""
        return x
    def addfield(self, pkt, s, val):
        return s+self.i2m(pkt, val)
    def getfield(self, pkt, s):
        return "",s
	
class SPAMField(StrField):
    islist=1
    def getfield(self, pkt, s):
        opsz = (pkt.dataofs-5)*4
        if opsz < 0:
            warning("bad dataofs (%i). Assuming dataofs=5"%pkt.dataofs)
            opsz = 0
        return s[opsz:],self.m2i(pkt,s[:opsz])
    def m2i(self, pkt, x):
        opt = []
        while x:
            onum = ord(x[0])
            
            if onum == 0:
                print "107 Internal Error"
                break
            if onum == 1:
                opt.append(("NOP",None))
                x=x[1:]
                continue
            olen = ord(x[1])
            oval = x[2:olen]
            if TCPOptions[0].has_key(onum):
                oname, ofmt = TCPOptions[0][onum]
                if ofmt:
                    oval = struct.unpack(ofmt, oval)
                    if len(oval) == 1:
                        oval = oval[0]
                opt.append((oname, oval))
            else:
                print "107 Internal Error"
                opt.append((onum, oval))
            x = x[olen:]
        return opt
    
    def i2m(self, pkt, x):
        opt = ""
        for oname,oval in x:
            if type(oname) is str:
                if oname == "NOP":
                    opt += "\x01"
                    print "101 Who are you ?? Plese use 'login' or 'new' commands"
                    continue
                elif TCPOptions[1].has_key(oname):
                    onum = TCPOptions[1][oname]
                    ofmt = TCPOptions[0][onum][1]
                    if ofmt is not None:
                        if type(oval) is not tuple:
                            print "102 Malformed command"
                            oval = (oval,)
                        oval = struct.pack(ofmt, *oval)
                else:
                    warning("option [%s] unknown. Skipped."%oname)
                    continue
            else:
                onum = oname
                if type(oval) is not str:
                    warning("option [%i] is not string."%onum)
                    continue
            opt += chr(onum)+chr(2+len(oval))+oval
        return opt+"\x00"*(3-((len(opt)+3)%4))
			
def shell_exec(account, command):
	exec(command)
		
class handler(SocketServer.StreamRequestHandler):
	
	def setfrom(self, param):
		if self.logged==False:
			print "101 Who are you ?? Plese use 'login' or 'new' commands"
			return 
		self.fake = param
		print "200 OK"
		pass
	def setdest(self, param):
		if self.logged==False:
			print "101 Who are you ?? Plese use 'login' or 'new' commands"
			return 
		self.dest = param
		if param=="local":
			temp = []
			files = os.listdir(".")
			for f in files:
				if f[:5] == "user_":
					temp.append(f[5:])
			print "mail to: %s"%temp
		print "200 OK"
		pass
	def spam(self, param):
		if self.logged==False:
			print "101 Who are you ?? Plese use 'login' or 'new' commands"
			return 
		if self.dest == None:
			print "105 Destination unknown"
			return
		print "- Write your spam message here."
		print "- The first line is the subject"
		print "- A line containing only a comma (.) will end the message"
		self.spamming = True;
		self.message = ""
		pass
	def send(self):
		try:
			f = open(self.username+".queue","a")
			f.write(self.message)
			f.write(".\n");
			f.close()
		except:
			print "107 Internal Error"
			return
		
		self.message = ""
	
	def stat(self, param):
		if self.logged==False:
			print "101 Who are you ?? Plese use 'login' or 'new' commands"
			return 
		try:
			f = open(self.username+".queue","r")
                        all = f.readlines()
			f.close()
		except:
			print "There are no mail in the queue"
			return
		
		print "Mail currently in the sending queue:"
		counter = 0
		header = True
		for line in all:
			if header:
				print "%d - %s"%(counter,line.strip())
				header = False
				counter += 1
			if line==".\n":
				header=True
		print "200 OK"
		pass
	def login(self, param):
		try:
			userid, password = param.split(" ",1)
		except Exception:
			print "102 Malformed command"
			return
		
		try:
			f = open("user_"+userid,"r")
			realpwd = f.readline()
			f.close()
		except:
			print "106 Userid or password incorrect"
			return
		realpwd = realpwd.strip()
		
		if realpwd==password:
			self.logged   = True;
			self.username = userid;
			print "200 OK"
		else:
			print "106 Userid or password incorrect"

	def whoami(self, param):
		print self.username

	def help(self, param):
		print banner
		print "login <userid> <passwd>                 Login into the spam server"
		print "new <userid> <passwd>                   Create a new account"
		print "from: <source>                          Set the source mail address"
		print "to: <source>                            Set the destination address"
		print "spam                                    Send a spam message"
		print "whoami                                  If you forget your name"
		print "stat                                    List the mails that are still in the queue"
		print "help                                    This command"
		
	def create(self, param):
		try:
			userid, password = param.split(" ",1)
		except Exception:
			print "102 Malformed command"
			return
		cmd = "grep"
		dict = "/usr/share/dict/american-english"
		
		if os.path.exists("./%s"%userid):
			print "104 Username already in use"
			return
		if len (password) < 5:
			print "103 Password too easy. Try something longer"
			return
		#elif len (password) > 15:
		#	print "103 Password too long (max 15 char)"
		#	return
		check = os.popen('%s "^%s$" %s'%(cmd,password,dict)).readlines()
		if len(check) > 0:
			print "103 Password too easy!! It matches the english word %s " %string.join(check)
			return
		
		try:
			f = open("user_"+userid,"w")
			f.write(password)
			f.close()
		except:
			print "107 Internal Error"
			return
		
		self.logged   = True
		self.username = userid	
		
		print "200 OK"
	
	def process(self, command):
		if self.spamming:
			if command.strip() == ".":
				print "200 OK"
				self.spamming = False
				self.send()
			else:
				self.message += command
			return
		
		command = command.strip()
		cmd = command.lower()
		
		if cmd == "exit":
			print "Bye Bye"
			self.stop = True
		
		elif cmd[:5] == "login":
			self.login(command[6:])
		elif cmd[:3] == "new":
			self.create(command[4:])
		elif cmd[:4] == "stat":
			self.stat(command[4:])
		elif cmd[:6] == "from: ":
			self.setfrom(command[6:])
		elif cmd[:4] == "spam":
			self.spam(command[4:])
		elif cmd[:4] == "to: ":
			self.setdest(command[4:])
		elif cmd[:6] == "whoami":
			self.whoami("")
	
		elif cmd[:4] == "help":
			self.help("")
		
		else:
			self.wfile.write("100 %s command unknown"%cmd)
			
	def handle (self):
		self.fake     = "nobody@nowhere.com"
		self.dest     = None
		self.spamming = False
		self.message  = ""
		self.logged   = False
		self.username = None
		
		sys.stdout = self.wfile
		self.stop = False
		self.wfile.write(banner)
		self.wfile.write("201 SDP server ready\n")
		
		while self.stop == False:
			try:
				cmd = self.rfile.readline()
			except socket.error: 
				break
			except KeyboardInterrupt:
				break
			try:
				self.process(cmd)
			except Exception, msg:
				print "Error %s"%msg
				break		
    
	def finish(self):
		self.wfile.flush()
		self.wfile.close()
		self.rfile.close()
		self.request.close()


if os.getuid()==0:
	#os.setuid(500)
	os.setuid(1002)
server = SocketServer.ForkingTCPServer(("", 4570), handler)
server.allow_reuse_address = True
print "SPAM Server is listening on port 4570"
server.serve_forever()


