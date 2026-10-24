#!/usr/bin/python
import re
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
        "curl/7.8 (i686-pc-linux-gnu) libcurl 7.8 (OpenSSL 0.9.6)",
        "Links (0.9x; Linux 2.4.7-10 i686)",
        "'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.A.B.C Safari/525.13'",
        random_string()]

class MuleUser(object):

    def __init__(self, ip):
        self.ip = ip
        self.base_url = 'http://%s:11111' % ip

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
            logging.info(checks)
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
        response = self.br.open(self.base_url + '/')
        self.br.select_form(nr=0)
        self.br['username'] = username
        self.br['password'] = password
        response = self.br.submit()
        tmp = response.read()
        if 'Welcome' not in tmp:
            logging.error('Could not sign in')
            logging.info(tmp)
            return False
        return False

    def check_main_page(self):
        logging.info('Checking main page')
        response = self.br.open(self.base_url)
        if not self.br.viewing_html():
            logging.error('Home page is not html')
            return True
        if not "Mule Alerting System" in response.read():
            logging.error('Could not recognize home page')
            return True
        logging.info('Main page is up')

    def check_sign_up(self, username, password):
        logging.info('Creating a user')
        response = self.br.open(self.base_url + '/register')
        self.br.select_form(nr=0)
        self.br['username'] = username
        self.br['password'] = password
        response = self.br.submit()
        if not 'User successfully registered.' in response.read():
            logging.error('Sign up was unsuccessful')
            return True
        logging.info('User created: %s / %s ' % (username, password))
        return False

    def check_flag(self):
        logging.info('Checking the flag')
        response = self.br.open(self.base_url + '/status')
        response_string = response.read()
        dom = string_to_dom(response_string)
        #import pdb;pdb.set_trace()
        try:
            for e in dom.cssselect('p'):
                tmp_re = re.search("Subject: (.*)", e.text)
                if tmp_re:
                    found_flag = tmp_re.group(1)
        except:
            logging.error('Flag is not where it should be')
            return True
        logging.info('Flag found')
        logging.info('The flag is still available')
        self.found_flag = found_flag
        return False

    def set_flag(self, flag):
        logging.info('Setting the new flag %s' % flag)
        print "url=%s" % (self.base_url + '/')
        self.br.open(self.base_url + '/')
        self.br.select_form(nr=0)
        self.br['subject'] = flag
        self.br['group'] = random_string()
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
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)
    user = MuleUser(sys.argv[2])
    if sys.argv[1] == 'set':
        auth = '%s:%s' % (random_string(), random_string())
        cookie = user.do_set_flag(cookie=auth, flag=sys.argv[3])
        print "COOKIE:%s" % auth
    elif sys.argv[1] == 'check':
        flag = user.do_get_flag(cookie=sys.argv[3])
        print 'FLAG:%s' % flag
    else:
        usage()


