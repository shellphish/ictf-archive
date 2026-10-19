#!/usr/bin/python
import mechanize
import logging
import random
import string
import sys
import os
random.seed(os.urandom(20))

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
        self.base_url = 'http://%s/ictf-2011-muleuser' % ip

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
        return any(checks)

    def do_get_flag(self, cookie, auth):
        self.reset_browser()
        self.found_flag = ''
        #logging.info('Checking flag routine started')
        username, password = self.split_cookie(auth)
        checks = [self.check_main_page(),
                  self.check_sign_up(username, password),
                  self.check_sign_in(username, password),
                  self.check_flag(cookie),]
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
            logging.error('Could not sign in')
            return False
        return False

    def check_main_page(self):
        #logging.info('Checking main page')
        response = self.br.open(self.base_url + '/index.php')
        if not self.br.viewing_html():
            logging.error('Home page is not html')
            return True
        if not "If you do not have an account" in response.read():
            logging.error('Could not recognize home page')
            return True
        #logging.info('Main page is up')

    def check_sign_up(self, username, password):
        #logging.info('Creating a user')
        response = self.br.open(self.base_url + '/register.php')
        self.br.select_form(nr=0)
        self.br['username'] = username
        self.br['pass'] = password
        self.br['repeat_pass'] = password
        response = self.br.submit()
        if not 'Your registration information was received.' in response.read():
            logging.error('Sign up was unsuccessful')
            return True
        #logging.info('User created: %s / %s ' % (username, password))
        return False

    def check_flag(self, cookie):
        #logging.info('Checking the flag')
        response = self.br.open(self.base_url + '/cgi-bin/viewmessage?msg=%s' % cookie)
        response_string = response.read()
        #import pdb;pdb.set_trace()
        try:
            found_flag = response_string.split("&lt;msgbody&gt;")[1].split("&lt;/msgbody&gt;")[0]
        except:
            logging.error('Flag is not where it should be')
            return True
        #logging.info('Flag found')
        #logging.info('The flag is still available')
        self.found_flag = found_flag
        return False

    def set_flag(self, flag):
        #logging.info('Setting the new flag %s' % flag)
        print "url=%s" % (self.base_url + '/cgi-bin/sendmessage')
        self.br.open(self.base_url + '/cgi-bin/sendmessage')
        self.br.select_form(nr=0)
        self.br['subject'] = "FLAG"
        self.br['body'] = flag
        submit = self.br.submit()
        try:
            cookie = submit.read().split("<div class=\"message\"><span class=\"app_msg_txt\">You can review the contents of the message <a href=\"viewmessage?msg=")[1].split("\">here</a></span></div>")[0]
            print 'COOKIE:%s' % cookie
        except:
            logging.error('Cookie is not where it should be')
            return True
        #logging.info('New flag is up')
class GetFlag():
  def execute(self, ip, port, flag_id, token):
    user = MuleUser(ip)
    auth = '%s:%s' % (random_string(), random_string())
    flag = user.do_get_flag(cookie=token, auth=auth)
    self.flag=flag
    self.error = 0
    self.error_msg = ""
  def result(self):
    return {'FLAG' : self.flag,
            'ERROR' : self.error,
            'ERROR_MSG' : self.error_msg,
           }
