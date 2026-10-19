# to be included in the files
import random
import string
import cPickle as pickle

state = { }
state['ppl'] = [ ]

def load_state():
	global state
	try:
		state = pickle.load(open("jobstate.p"))
	except Exception:
		state = { }
		state['ppl'] = [ ]

def save_state():
	global state
	pickle.dump(state, open("jobstate.p", "w"))

def random_word():
	return random.sample(open("/usr/share/dict/american-english").readlines(), 1)[0].strip()[:10]

def random_pin():
	return str(random.randint(0, 99))

def random_secret():
	FLAG_POSSIBILITIES = string.ascii_uppercase + string.digits + string.ascii_lowercase
	new_flag = ''.join(random.choice(FLAG_POSSIBILITIES) for x in range(13))
	return "FLG" + new_flag

def reset(child):
	print "RESET"
	child.sendline("1")
	child.expect("continue")
	child.sendline("")

def register_account(child, i=-1, person=None):
	print "REGISTER",person
	if person == None:
		bank = random.sample([ a[0] for a in state['ppl'] ], 1)[0]
		lvl = 0
	else:
		bank = person[0]
		lvl = person[1]

	uid = random_word()
	pin = random_pin()
	lvl = random.randint(0, lvl)
	
	child.sendline("3")
	child.expect("with?")
	child.sendline(bank)
	child.expect("username:")
	child.sendline(uid)
	child.expect("PIN")
	child.sendline(pin)
	child.expect("level:")
	child.sendline(str(lvl))
	child.expect("continue.")
	child.sendline("")

	state['ppl'].append([bank, lvl, uid, pin, ""])

def register_bank(child, i=-1, person=None):
	print "REG_BANK",person

	if person == None:
		bank = random_word()
		n = random_word()
		p = random_pin()
	else:
		bank, lvl, n, p, m = person

	child.sendline("4")
	child.expect("bank name")
	child.sendline(bank)
	if child.expect(["CFO:", "registered!"]) == 1:
		child.sendline("")
		register_bank(child)
		return
	child.sendline(n)
	child.expect("PIN")
	child.sendline(p)
	child.expect("Added")
	child.expect("continue")
	child.sendline("")

	print "NEW USER"
	state['ppl'].append([bank, 2, n, p, ""])

def log_in(child, i, person):
	print "LOGIN",person
	bank, lvl, n, p, m = person

	child.sendline("5")
	child.expect("username")
	child.sendline(n)
	child.expect("PIN")
	child.sendline(p)
	child.expect("Resulting access")
	child.sendline("")

def show_maiden_name(child, i, person):
	print "SHOW_MAIDEN",person
	bank, lvl, n, p, m = person

	child.sendline("6")
	child.expect("maiden name is: ")
	name = child.read(50)
	child.expect("continue")
	child.sendline("")

	return name.strip()

def set_maiden_name(child, i, person, set_m=None):
	print "SET_MAIDEN",person,set_m
	bank, lvl, n, p, m = person

	if set_m == None:
		set_m = random_secret()

	if 'flagee' in state and bank == state['flagee'][0] and n == state['flagee'][2]:
		return

	child.sendline("7")
	child.expect("Please enter")
	child.sendline(set_m)
	child.expect("continue.")
	child.sendline("")

	state['ppl'][i][4] = set_m

def fetch_maiden_name_entry(child, i, person):
	print "FETCH_MAIDEN_ENTRY",person
	bank, lvl, n, p, m = person

	others = [ a for a in state['ppl'] if a[0] == bank ]
	if len(others) == 0:
		return
	chosen = random.sample(others, 1)[0]

	child.sendline("8")
	child.expect("username")
	child.sendline(chosen[2])
	child.expect(chosen[4])
	child.expect("continue")
	child.sendline("")

def set_maiden_name_entry(child, i, person, set_m=None):
	print "SET_MAIDEN_ENTRY",person
	if set_m == None:
		set_m = random_secret()

	bank, lvl, n, p, m = person

	others = [ a for a in state['ppl'] if a[0] == bank ]
	#print others
	if len(others) == 0:
		return
	chosen = random.sample(others, 1)[0]

	if 'flagee' in state and bank == state['flagee'][0] and chosen[2] == state['flagee'][2]:
		return

	child.sendline("9")
	child.expect("username:")
	child.sendline(chosen[2])
	child.expect("maiden name:")
	child.sendline(set_m)
	child.expect("continue")
	child.sendline("")

	chosen[4] = set_m

def list_users(child, i, person):
	print "LIST",person
	bank, lvl, n, p, m = person

	other_names = [ a[2] for a in state['ppl'] if a[0] == bank ]
	#print other_names
	if len(other_names) == 0:
		return

	child.sendline("10")
	for _ in other_names:
		child.expect(other_names)

	child.expect("continue")
	child.sendline("")

actions = { }
actions[-2] = [ register_account, register_bank ]
actions[-1] = [ register_account, register_bank, log_in ]
actions[0] = [ show_maiden_name, set_maiden_name ]
actions[1] = [ fetch_maiden_name_entry, set_maiden_name_entry ]
actions[2] = [ list_users ]

def normal_user(child, i, person, nosurprises=False):
	bank, lvl, n, p, m = person

	choices = [ -1,-1,-1,-1 ]
	if not nosurprises:
		choices += [ -2 ]
	if lvl >= 0:
		choices += [ 0,0,0,0,0,0,0 ]
	if lvl >= 1:
		choices += [ 1,1,1,1 ]
	if lvl >= 2:
		choices += [ 2,2 ]

	num_actions = random.randint(0, 4)
	for _ in range(num_actions):
		act_idx = random.sample(choices, 1)[0]
		random.sample(actions[act_idx], 1)[0](child, i, person)

def normal_connection(child):
	num_users = random.randint(0, 2)
	for _ in range(num_users):
		u = random.randint(0, len(state['ppl']) - 1)
		log_in(child, u, state['ppl'][u])
		normal_user(child, u, state['ppl'][u])
