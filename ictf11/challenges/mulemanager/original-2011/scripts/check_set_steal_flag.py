#!/usr/bin/env python
import mechanize
import logging
import random
import string
import sys

logging.basicConfig(level=logging.INFO)


################################################################################
### UTILS
################################################################################

def random_string():
    return ''.join(random.choice(string.ascii_lowercase)
                for x in range(random.choice(range(10, 20))))


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
### ACTUAL SCRIPT
################################################################################

USER_AGENTS = [
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6",
        "Mozilla/4.0 (compatible; MSIE 6.0; MSIE 5.5; Windows NT 5.1) Opera 7.02 [en]",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1",
        random_string()]

class MuleUser(object):

    def __init__(self, ip):
        self.ip = ip
        self.base_url = 'http://%s' % ip

    def split_cookie(self, secret):
        return secret.split(':')

    def do_set_flag(self, cookie, flag):
        self.reset_browser()
        logging.info('Setting flag routine started')
        username, password = self.split_cookie(cookie)
        checks = [self.check_main_page(),
                  self.check_sign_up(username, password),
                  self.check_sign_in(username, password),
                  self.set_flag(flag)]
        logging.info('Setting flag routine completed')
        return any(checks)

    def do_get_flag(self, cookie):
        self.reset_browser()
        self.found_flag = ''
        logging.info('Checking flag routine started')
        username, password = self.split_cookie(cookie)
        checks = [self.check_main_page(),
                  self.check_sign_in(username, password),
                  self.check_flag(),]
        logging.info('Checking flag routine completed')
        if any(checks):
            logging.info('Some steps failed')
        return self.found_flag

    def reset_browser(self):
        self.br = mechanize.Browser()
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', random.choice(USER_AGENTS))]

    def check_sign_in(self, username, password):
        self.reset_browser()
        logging.info('Signing in with %s / %s' % (username, password))
        response = self.br.open(self.base_url + '/login.php')
        self.br.select_form(nr=0)
        self.br['username'] = username
        self.br['password'] = password
        response = self.br.submit()
        if 'Mule Manager allows you to mass mail your fellows mules in case of emergency.' in response.geturl():
            logging.error('Could not sign in')
            return False
        return False

    def check_main_page(self):
        logging.info('Checking main page')
        response = self.br.open(self.base_url)
        if not self.br.viewing_html():
            logging.error('Home page is not html')
            return True
        if not "If you do not have an account" in response.read():
            logging.error('Could not recognize home page')
            return True
        logging.info('Main page is up')

    def check_sign_up(self, username, password):
        logging.info('Creating a user')
        response = self.br.open(self.base_url + '/register.php')
        self.br.select_form(nr=0)
        self.br['username'] = username
        self.br['pass'] = password
        self.br['repeat_pass'] = password
        response = self.br.submit()
        if not 'Your registration information was received.' in response.read():
            logging.error('Sign up was unsuccessful')
            return True
        logging.info('User created: %s / %s ' % (username, password))
        return False

    def check_flag(self):
        logging.info('Checking the flag')
        response = self.br.open(self.base_url + '/contact.php')
        response_string = response.read()
        if "We currently have the following ways of contacting you:" not in response_string:
            logging.error('The /contact.php page is not containing the correct text')
        dom = string_to_dom(response_string)
        try:
            found_flag =  dom.cssselect('td#the_address')[0].text.strip()
        except:
            logging.error('Flag is not where it should be')
            return True
        logging.info('Flag found')
        logging.info('The flag is still available')
        self.found_flag = found_flag
        return False

    def set_flag(self, flag):
        logging.info('Setting the new flag %s' % flag)
        self.br.open(self.base_url + '/contact.php')
        self.br.select_form(nr=0)
        self.br['address'] = flag
        self.br['carrier'] = random.choice(['Verizon', 'Tmobile', 'Sprint', random_string(), ''])
        self.br.submit()
        logging.info('New flag is up')


def usage():
    print """
USAGE:
    get IP COOKIE
    set IP FLAG
    test IP
"""

if __name__ == '__main__':
    if len(sys.argv) != 4:
        usage()
        sys.exit(1)
    user = MuleUser(sys.argv[2])
    if sys.argv[1] == 'set':
        cookie = '%s:%s' % (random_string(), random_string())
        user.do_set_flag(cookie=cookie, flag=sys.argv[3])
        print 'COOKIE:%s' % cookie
    elif sys.argv[1] == 'get':
        flag = user.do_get_flag(cookie=sys.argv[3])
        print 'FLAG:%s' % flag
    elif sys.argv[1] == 'test':
        cookie = '%s:%s' % (random_string(), random_string())
        user.do_set_flag(cookie=cookie, flag="FLAG!")
        flag = user.do_get_flag(cookie=cookie)
        print 'FLAG:%s' % flag
    else:
        usage()

