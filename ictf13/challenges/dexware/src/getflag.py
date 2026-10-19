
from telnetlib import Telnet
from random import randrange
import re
import time
import base64
import traceback
import IPython

DEBUG = True

def generate_new_flag():
    import string, random
    FLAG_POSSIBILITIES = string.ascii_uppercase + string.digits + string.ascii_lowercase
    new_flag = ''.join(random.choice(FLAG_POSSIBILITIES) for x in range(13))
    return "FLG" + new_flag

def send_recv_msg(s, msg):
    s.send(msg + '\n')
    ans = s.recv(128).strip()
    return ans

def get_msg(s):
    msg = s.recv(128).strip()
    return msg

def gen_new_password():
    return 'password-123'

def gen_new_formula():
    return generate_new_flag()

def read_until_prompt(t):
    ans = t.read_until('Insert number: ')
    return ans

def read_until(t, msg):
    ans = t.read_until(msg)
    return ans

def extract_formula_id(t):
    ans = read_until_prompt(t)
    formula_id = None
    for line in ans.split('\n'):
        m = re.search('Generated new formula ID: ([0-9a-f]+)', line)
        if not m: continue
        formula_id = m.group(1)
    assert formula_id is not None
    return formula_id

def extract_formula(t):
    ans = read_until_prompt(t)
    formula = None
    for line in ans.split('\n'):
        m = re.search('The formula is: (\w+)', line)
        if not m: continue
        formula = m.group(1)
    assert formula is not None
    return formula

def add_formula(t, formula):
    password = gen_new_password()
    if DEBUG: print 'add_formula - %s - %s' % (password, formula)
    t.write('2\n%s\n%s\n' % (password, formula))
    formula_id = extract_formula_id(t)
    return formula_id, password

def get_formula(t, formula_id, password):
    if DEBUG: print 'get_formula - %s' % formula_id
    t.write('3\n%s\n%s\n' % (formula_id, password))
    formula = extract_formula(t)
    return formula

def list_formulas(t):
    if DEBUG: print 'list_formula'
    t.write('1\n')
    ans = read_until_prompt(t)
    return ans

def leak_formula_from_list(t, flag_id):
    ans = list_formulas(t)
    formula = None
    for line in ans.split('\n'):
        if line.find(flag_id) >= 0:
            formula = line.split(' - ')[-1]
            break
    assert formula is not None
    return formula

def do_quit(t):
    if DEBUG: print 'do_quit'
    t.write('6\n')
    read_until(t, 'Bye.')

def do_upgrade(t):
    t.write('4\n')
    ans = read_until_prompt(t)
    return ans

def do_about(t):
    t.write('5\n')
    ans = read_until_prompt(t)
    return ans

class GetFlag():

    DEBUG = False

    def do_getflag(self, t, flag_id, token):
        read_until_prompt(t)
        flag = get_formula(t, flag_id, token)
        do_quit(t)
        return flag

    def execute(self, ip, port, flag_id, token):
        error = 0
        error_msg = ''
        flag = ''
        try:
            t = Telnet(ip, port)
            flag = self.do_getflag(t, flag_id, token)
            error = 0 if flag else 1
            error_msg = '' if flag else 'script malfunctioning'
        except Exception as e:
            error = 2
            error_msg = 'EXCEPTION: %s' % str(traceback.format_exc())

        self.flag = flag
        self.error = error
        self.error_msg = error_msg

    def result(self):
        return {'FLAG' : self.flag,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }
