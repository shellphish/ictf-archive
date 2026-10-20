import mechanize
import random
import string
from random import Random
import os
random.seed(os.urandom(20))
def random_string():
    return ''.join(random.choice(string.ascii_lowercase)
                for x in range(random.choice(range(10, 20))))
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
    def do_check_flag(self, email, password):
        self.ensure_logged_out()
        checks = [self.check_main_page(),
                  self.check_sign_in(email, password),
                  self.check_get_remote_payment(),
                  self.check_flag(),]
        return any(checks)
    def ensure_logged_out(self):
        self.br = mechanize.Browser()
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', random.choice(USER_AGENTS))]
    def check_sign_in(self, email, password):
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
def split_cookie(cookie):
    return cookie.split(':')
def get_flag(ip, cookie):
    customer = eGoatCostumer(ip)
    email, password = split_cookie(cookie)
    customer.do_check_flag(email, password)
    return customer.found_flag
class GetFlag():
  def execute(self, ip, port, flag_id, token):
    flag = get_flag(ip=ip,
                    cookie=flag_id + ":" + token)
    self.flag = flag
    self.error = 0
    self.error_msg = ""
  def result(self):
    return {'FLAG' : self.flag,
            'ERROR' : self.error,
            'ERROR_MSG' : self.error_msg,
           }
