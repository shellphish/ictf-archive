#!/usr/bin/env python
import mechanize
#import logging
import random
import string
import sys
import os
random.seed(os.urandom(20))

#logging.basicConfig(level=logging.INFO)


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
        self.base_url = 'http://%s:7899/' % ip

    def split_cookie(self, secret):
        return secret.split(':')

    def do_set_flag(self, cookie, flag):
        self.reset_browser()
        #logging.info('Setting flag routine started')
        username, password = self.split_cookie(cookie)
        checks = [self.check_main_page(),
                  self.check_sign_up(username, password),
                  self.check_sign_in(username, password),
                  self.set_flag(flag)]
        #logging.info('Setting flag routine completed')
        return all(checks)

    def do_get_flag(self, cookie):
        self.reset_browser()
        self.found_flag = ''
        #logging.info('Checking flag routine started')
        username, password = self.split_cookie(cookie)
        checks = [self.check_main_page(),
                  self.check_sign_in(username, password),
                  self.check_flag(),]
        #logging.info('Checking flag routine completed')
        #if any(checks):
            #logging.info('Some steps failed')
        return self.found_flag

    def reset_browser(self):
        self.br = mechanize.Browser()
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', random.choice(USER_AGENTS))]

    def check_sign_in(self, username, password):
        self.reset_browser()
        #logging.info('Signing in with %s / %s' % (username, password))
        response = self.br.open(self.base_url + '/login.php')
        self.br.select_form(nr=0)
        self.br['username'] = username
        self.br['password'] = password
        response = self.br.submit()
        if 'Mule Manager allows you to mass mail your fellows mules in case of emergency.' in response.geturl():
            #logging.error('Could not sign in')
            return False
        return True

    def check_main_page(self):
        #logging.info('Checking main page')
        response = self.br.open(self.base_url + '/index.php')
        if not self.br.viewing_html():
            #logging.error('Home page is not html')
            return False
        if not "If you do not have an account" in response.read():
            #logging.error('Could not recognize home page')
            return False
        #logging.info('Main page is up')
        return True

    def check_sign_up(self, username, password):
        #logging.info('Creating a user')
        response = self.br.open(self.base_url + '/register.php')
        self.br.select_form(nr=0)
        self.br['username'] = username
        self.br['pass'] = password
        self.br['repeat_pass'] = password
        response = self.br.submit()
        if not 'Your registration information was received.' in response.read():
            #logging.error('Sign up was unsuccessful')
            return False
        #logging.info('User created: %s / %s ' % (username, password))
        return True

    def check_flag(self):
        #logging.info('Checking the flag')
        response = self.br.open(self.base_url + '/contact.php')
        response_string = response.read()
#        if "We currently have the following ways of contacting you:" not in response_string:
            #logging.error('The /contact.php page is not containing the correct text')
        try:
            found_flag = response_string.split("<tr><td id=\"the_type\">sms</td><td id=\"the_address\">")[-1].split("</td><td id=\"the_carrier\">")[0]
        except:
            #logging.error('Flag is not where it should be')
            return False
        #logging.info('Flag found')
        #logging.info('The flag is still available')
        self.found_flag = found_flag
        return True

    def set_flag(self, flag):
        #logging.info('Setting the new flag %s' % flag)
        self.br.open(self.base_url + '/contact.php')
        self.br.select_form(nr=0)
        self.br['address'] = flag
        self.br['carrier'] = random.choice(['Verizon', 'Tmobile', 'Sprint', random_string(), ''])
        self.br.submit()
        #logging.info('New flag is up')
        return True

class SetFlag():
  def execute(self, ip, port, flag):
    user = MuleUser(ip)
    flag_id = random_string()
    token = random_string()
    cookie = '%s:%s' % (flag_id, token)
    ret = user.do_set_flag(cookie=cookie, flag=flag)
    if ret:
        self.flag_id = flag_id
        self.token = token
        self.error = 0
        self.error_msg = ""
    else:
        self.flag_id = flag_id
        self.token = token
        self.error = 42
        self.error_msg = "Failed to set flag."

  def result(self):
    return {'FLAG_ID' : self.flag_id,
            'TOKEN' : self.token,
            'ERROR' : self.error,
            'ERROR_MSG' : self.error_msg,
           }

if __name__ == "__main__":
    import sys
    sf = SetFlag()
    sf.execute(sys.argv[1], 7899, sys.argv[2])
    print sf.result()

