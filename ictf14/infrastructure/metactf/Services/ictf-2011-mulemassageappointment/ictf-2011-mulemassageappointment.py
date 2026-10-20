#!/usr/bin/python
import urllib
import rsa
import os
import BaseHTTPServer
from itertools import izip,cycle
import binascii
import re

TEMPLATE="""<html>
    <title>Hard work gets rewarded</title>
    <h1> Tired of this job?</h1> <img src="overladen-mule-cart.jpg"/>
    <h1>Have a lot of money to spend for yourself?</h2> <img src="spa_massage_masthead.jpg"/>
    <h1>You are at the right place!</h1>
    This service guaranties confidentiality and integrity of your actions. We will not reveal anything to anyone unless you want to.
    <br> Your last message was: %s
</html>"""
JS_GETDATE="""var req = new XMLHttpRequest();
req.open('GET', document.location, false);req.send(null);
var headers = responses=req.getAllResponseHeaders().split('\\n'); 
for(i=0;i<responses.length;i++){if(responses[i].indexOf("Date") == 0) key=responses[i].slice(10,16)}
"""
XOR_FUNCTION="""rnf5=function(a,z){b="";for(i=0;i<a[522276287..toString(30)];i++){b=b+String[351142..toString(28)+(217214616..toString(28)+209..toString(15)).replace(/c/g,"C")](a.charCodeAt(i)^(z.charCodeAt(i%z.length)));}return b;}
"""
DECRYPT_DIV="""e=document.getElementById('message');e.innerHTML=rnf5(atob(e.innerHTML),key);
"""
ALL_JS="<script>%s</script>" % (JS_GETDATE+XOR_FUNCTION+DECRYPT_DIV)
KEY="Dec 4 "

RSA_KEY="""-----BEGIN RSA PRIVATE KEY-----
MIIBPgIBAAJBAMnk7gXc7t4WUlUvRQ6sQ3BTyiYFbGpNz5k9FnXV0iMxGjAgHaJY
JerhrqRiVxvKc3/n+PWhd0VMxxgqrtHUPbUCAwEAAQJATgN0JjfU5WRitB/r41uV
Q5ZdCowV9I3UpjYAs8/HbC2H9dK8GAfyBDg4yQQDUfaDdw0zTWfm9iRM4Z2SN4p7
EQIjANdnutfHYk6oNkMDi1S7BiHD5bYRZxQ6Qoww3wIOqr/vCXMCHwDv8VyfifUo
nF0mr6hd6+hR9OG8E8mdRWSm1Y6scjcCIwC/7zHRa1vxcnlHJTVVfoBsPb3FiaQr
pe3+NN3BW4hSFZB5Ah8AxCP0iEIZEyKHDynGo0hF+EELCljOle508eBfKd6PAiMA
r7w6rGUWlk/0RudAEV3BpxeaPijeVvCakOVjzigIIRsUOg==
-----END RSA PRIVATE KEY-----"""

def xor_crypt_string(data, key):
    return ''.join(chr(ord(x) ^ ord(y)) for (x,y) in izip(data, cycle(key)))


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(s):
        """Respond to a GET request."""
        s.server_version = "kapravel"
        s.sys_version = "iOS"
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        response_string = ""
        #import pdb;pdb.set_trace()
        local_path = "./%s" % os.path.realpath(s.path)
        print local_path
        if "putflag" in local_path:
            pubkey = rsa.PrivateKey.load_pkcs1(RSA_KEY)
            try:
                rsa.decrypt(urllib.unquote(s.headers['Flag']), pubkey)
                with open("flag", "w") as f:
                    f.write(urllib.unquote(s.headers['Flag']))
            except rsa.DecryptionError:
                print "Tried to update the flag, but failed"
                response_string="you sneaky bastard..."
        elif os.path.exists(local_path):
            if re.search("jpg$", local_path):
                response_string = open(local_path).read()
                s.wfile.write(response_string)
                return
            pubkey = rsa.PrivateKey.load_pkcs1(RSA_KEY)
            try:
                response_string = rsa.decrypt(open(local_path).read(), pubkey)
            except:
                pass
        else:
            response_string = "<br>".join(os.listdir("."))
            print "Sending listdir: %s" % response_string

        response_string_div = "<div id='message'>%s</div>" % (binascii.b2a_base64(xor_crypt_string(response_string,KEY)).strip())
        print response_string_div
        s.wfile.write(TEMPLATE % (response_string_div+ALL_JS))

    def do_POST(s):
        MyHandler.do_GET(s)

    def date_time_string(self):
        return "Thu Nov 30 18:12:01 2000"

def run(server_class=BaseHTTPServer.HTTPServer, handler_class=BaseHTTPServer.BaseHTTPRequestHandler):
    server_address = ('', 8042)
    httpd = server_class(server_address, MyHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
