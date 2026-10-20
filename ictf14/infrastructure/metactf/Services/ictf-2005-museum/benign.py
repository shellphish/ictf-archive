import socket
import sys
sys.path.insert(0,'.')
from utility import pybrowse
class Benign():

    def do_benign(self, s, username, password):
        pass
        
    def execute(self, ip, port, flag_id, token):
        self.error = 0
        self.error_msg = ''
        self.flag_id = ""
        self.token = ""
        getPage=pybrowse.Browser("http://"+ip+ ":" + str(port) + "/")
        getPage.open()
        getPage2a=pybrowse.Browser("http://" + ip + ":" + str(port) + "/search.html")
        getPage2a.open()
        getPage2=pybrowse.Browser("http://" + ip + ":" + str(port) + "/cgi-bin/museum_search.pl?keyword=foo")
        getPage2.open()
        getPage3=pybrowse.Browser("http://" + ip + ":" + str(port) + "/cgi-bin/museum_search.pl?keyword=foo")
        getPage3.open()
        getFlagPage=pybrowse.Browser("http://" +ip+ ":" + str(port) + "/cgi-bin/museum_admin.pl?first=" + flag_id + "&last=" + token + "&password=unbreakable")
        getFlagPage.open()
        self.flag_id = flag_id
        self.token = token
        self.error = 0
        self.error_msg = None
        
    def result(self):
        if self.error == 0:
            return {'FLAG_ID' : self.flag_id,
                'TOKEN' : self.token,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }
        else:
            return {
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }
