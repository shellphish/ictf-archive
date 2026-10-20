import mechanize
import random
import string
from random import Random
import copy
import os
import irclib
random.seed(os.urandom(20))
def random_string():
    return ''.join(random.choice(string.ascii_lowercase)
                for x in range(random.choice(range(10, 20))))
port = 6667
channel = '#egoats_'
def say_in_irc(message,ip):
    irc = irclib.IRC()
    server = irc.server()
    server.connect ( ip, port, random_string(), ircname = random_string() )
    server.join ( channel )
    server.privmsg(channel, message)
    server.quit('FLAG planted')
generator = Random()
generator.seed()
def random_credit_card(type=""):
        def credit_card_number(generator, prefixList, length):
            def _completed_number(prefix, length):
                ccnumber = prefix
                while len(ccnumber) < (length - 1):
                    digit = generator.choice(['0',  '1', '2', '3', '4', '5', '6', '7', '8', '9'])
                    ccnumber.append(digit)
                sum, pos = (0, 0)
                reversedCCnumber = []
                reversedCCnumber.extend(ccnumber)
                reversedCCnumber.reverse()
                while pos < length - 1:
                    odd = int( reversedCCnumber[pos] ) * 2
                    if odd > 9:
                        odd -= 9
                    sum += odd
                    if pos != (length - 2):
                        sum += int( reversedCCnumber[pos+1] )
                    pos += 2
                checkdigit = ((sum / 10 + 1) * 10 - sum) % 10
                ccnumber.append( str(checkdigit) )
                return ''.join(ccnumber)
            result = []
            ccnumber = copy.copy( generator.choice(prefixList) )
            result.append( _completed_number(ccnumber, length) )
            return result
        if type in "visa":
            visaPrefixList = [['4','0','2','4', '0', '0', '7', '1'],]
            return credit_card_number(generator, visaPrefixList, 16)
        elif type is "bogus":
            amexPrefixList = [['3','4'],['3', '7']]
            return credit_card_number(generator, amexPrefixList, 16)
        elif type is "master":
            mastercardPrefixList = [['5','1'],['5','2'],['5','3'],['5','4'],['5','5']]
            return credit_card_number(generator, mastercardPrefixList, 16)
USER_AGENTS = [
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6",
        "Mozilla/4.0 (compatible; MSIE 6.0; MSIE 5.5; Windows NT 5.1) Opera 7.02 [en]",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1",
        "curl/7.8 (i686-pc-linux-gnu) libcurl 7.8 (OpenSSL 0.9.6)",
        "Links (0.9x; Linux 2.4.7-10 i686)",
        "'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.A.B.C Safari/525.13'",
        random_string()]
class eGoatCostumer(object):
    def __init__(self, ip):
        self.ip = ip
        self.base_url = 'http://%s:53550/' % ip
        self.ensure_logged_out()
    def do_set_flag(self, email, password, flag):
        self.ensure_logged_out()
        checks = [self.check_main_page(),
                  self.check_sign_up(email, password),
                  self.check_make_payment(),
                  self.check_get_remote_payment(),
                  self.set_flag(flag),
                  self.check_flag(),]
        return any(checks)
    def ensure_logged_out(self):
        self.br = mechanize.Browser()
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', random.choice(USER_AGENTS))]
    def check_sign_in(self, email, password):
        logging.info('Signing in with %s / %s' % (email, password))
        response = self.br.open(self.base_url + 'users/sign_in')
        self.br.select_form(nr=0)
        self.br['user[email]'] = email
        self.br['user[password]'] = password
        response = self.br.submit()
        if 'sign_in' in response.geturl():
            logging.error('Could not sign in')
            return False
        return False
    def check_main_page(self):
        response = self.br.open(self.base_url)
        if not self.br.viewing_html():
            logging.error('Home page is not html')
            return True
        if not "goat owner" in response.read():
            logging.error('Could not recognize home page')
            return True
        return False
    def check_sign_up(self, email, password):
        response = self.br.open(self.base_url + 'users/sign_up')
        self.br.select_form(nr=0)
        self.br['user[email]'] = email
        self.br['user[password]'] = password
        self.br['user[password_confirmation]'] = password
        response = self.br.submit()
        if 'sign_up' in response.geturl():
            logging.error('Could not sign up')
            return True
        if not 'Logout' in response.read():
            logging.error('Sign up was unsuccessful')
            return True
        return False
    def check_make_payment(self):
	while True:
	  try:
            response = self.br.open(self.base_url + 'payments/new')
            self.br.select_form(nr=0)
            card_type = random.choice(['bogus', 'master', 'visa'])
            self.br['payment[amount]'] = str(random.choice(xrange(1, 100)))
            self.br['payment[credit_card_attributes][number]'] = str(random_credit_card(card_type))
            self.br['payment[credit_card_attributes][month]'] =  str(random.choice(xrange(1, 13)))
            self.br['payment[credit_card_attributes][year]'] =   str(random.choice(xrange(2013, 2019)))
            self.br['payment[credit_card_attributes][first_name]'] = random_string()
            self.br['payment[credit_card_attributes][last_name]'] = random_string()
            self.br.form.set_all_readonly(False)
            self.br['payment[credit_card_attributes][type]'] = card_type
            response = self.br.submit()
            self.br.open(self.base_url + 'payments/start_remote_payment')
	    break
          except:
            pass
        response = self.br.open(self.base_url + 'payments/payment_successful')
        try:
            token = response.read().split("<b class='rainbow' id='token'>")[-1].split("</b>.")[0]
        except:
            logging.error('Token not found on payment_successful page')
            return True
        if not token:
            logging.error('Token is empty on payment_successful page')
        return False
    def check_get_remote_payment(self):
        response = self.br.open(self.base_url + 'users/me')
        try:
            remote_payment_id = response.read().split("<li class='offer' id=")[-1].split(">")[0]
        except:
            logging.error('Could not find the remote payment id of my transaction')
            return True
        if not remote_payment_id:
            logging.error('Transaction id is empty')
            return True
        self.remote_payment_id = remote_payment_id
        return False
    def check_flag(self):
        response = self.br.open(self.base_url + 'remote_payments/%s' % self.remote_payment_id)
        try:
            found_flag = response.read().split("<b id='token'>")[-1].split("</b>")[0]
        except:
            logging.error('Token not found on remote_payments page')
            return True
        self.found_flag = found_flag
        return False
    def set_flag(self, flag):
        self.br.open(self.base_url + 'remote_payments/%s/edit' % self.remote_payment_id)
        self.br.select_form(nr=0)
        self.br['remote_payment[token]'] = flag
        self.br.submit()
def split_cookie(cookie):
    return cookie.split(':')
def set_flag(ip, cookie, flag):
    customer = eGoatCostumer(ip)
    email, password = split_cookie(cookie)
    if not customer.do_set_flag(email, password, flag):
        say_in_irc(email,ip)
class SetFlag():
  def execute(self, ip, port, flag):
    email = '%s@%s.%s' % (random_string(),
            random.choice([random_string(), 'gmail', 'hotmail', 'yahoo','google', 'redtube']),
            random.choice([random_string(), 'com', 'info', 'edu', 'jp', 'it']))
    self.flag_id = email
    self.token = random_string()
    cookie = '%s:%s' % (self.flag_id, self.token)
    set_flag(ip=ip,
             cookie=cookie,
             flag=flag)
    #self.token = cookie
    self.error = 0
    self.error_msg = ""
  def result(self):
    return {'FLAG_ID' : self.flag_id,
            'TOKEN' : self.token,
            'ERROR' : self.error,
            'ERROR_MSG' : self.error_msg,
           }
