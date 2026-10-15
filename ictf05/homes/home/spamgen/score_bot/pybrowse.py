#!/usr/bin/python

import random
import string

class BrowserPersonality:
  def __init__(self, name, headers):
     self.name = name
     self.headers = headers

  def getHeaders(self, host, referer = None, clength = 0):
     ret = []
     for h in self.headers:
        (key,val) = h
        l = string.lower(key)
        if l == "host":
           ret.append((key, host))
        elif l == "referer":
           if referer:
              ret.append((key,referer))
        elif l == "content-type":
           if clength > 0:
              ret.append(h)
        elif l == "content-length":
           if clength > 0:
              ret.append((key,str(clength)))
        else:
           ret.append(h)

     return  ret



all_browsers = [ BrowserPersonality("Konquerror/ Linux",[
                                   ("Connection", "Keep-Alive"),
                                   ("User-Agent", "Mozilla/5.0 (compatible; Konqueror/3.3; Linux) (KHTML, like Gecko)"),
                                   ("Referer", "http://192.168.5.2:8000/"),
                                   ("Pragma", "no-cache"),
                                   ("Cache-control", "no-cache"),
                                   ("Accept", "text/html, image/jpeg, image/png, text/*, image/*, */*"),
                                   ("Accept-Encoding", "x-gzip, x-deflate, gzip, deflate"),
                                   ("Accept-Charset", "iso-8859-1, utf-8;q=0.5, *;q=0.5"),
                                   ("Accept-Language", "en"),
                                   ("Host", "192.168.5.2:8000"),
                                   ("Content-Type", "application/x-www-form-urlencoded"),
                                   ("Content-Length", "36") ]),

                BrowserPersonality("Mozilla/ Linux",[
                                   ("Host", "192.168.5.2:8000"),
                                   ("User-Agent", "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.3) Gecko/20041008"),
                                   ("Accept", "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"),
                                   ("Accept-Language", "en-us,en;q=0.5"),
                                   ("Accept-Encoding", "gzip,deflate"),
                                   ("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.7"),
                                   ("Keep-Alive", "300"),
                                   ("Connection", "keep-alive"),
                                   ("Referer", "http://192.168.5.2:8000/"),
                                   ("Content-Type", "application/x-www-form-urlencoded"),
                                   ("Content-Length", "36") ]),


                BrowserPersonality("Firefox/ Linux",[
                                   ("Host", "192.168.5.2:8000"),
                                   ("User-Agent", "Mozilla/5.0 (X11; U; Linux i686; rv:1.7.3) Gecko/20041001 Firefox/0.10.1"),
                                   ("Accept", "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"),
                                   ("Accept-Language", "en-us,en;q=0.5"),
                                   ("Accept-Encoding", "gzip,deflate"),
                                   ("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.7"),
                                   ("Keep-Alive", "300"),
                                   ("Connection", "keep-alive"),
                                   ("Referer", "http://192.168.5.2:8000/"),
                                   ("Content-Type", "application/x-www-form-urlencoded"),
                                   ("Content-Length", "36") ]),


                BrowserPersonality("Safari/ OSX",[
                                   ("Host", "192.168.5.2:8000"),
                                   ("Connection", "close"),
                                   ("Referer", "http://192.168.5.2:8000/"),
                                   ("User-Agent", "Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en) AppleWebKit/125.5.5 (KHTML, like Gecko) Safari/125.11"),
                                   ("Accept", "*/*"),
                                   ("Accept-Encoding", "gzip, deflate;q=1.0, identity;q=0.5, *;q=0"),
                                   ("Accept-Language", "en, ja;q=0.92, ja-jp;q=0.96, fr;q=0.88, de-de;q=0.85, de;q=0.81, es;q=0.77, it-it;q=0.73, it;q=0.69, nl-nl;q=0.65, nl;q=0.62, sv-se;q=0.58, sv;q=0.54, no-no;q=0.50, no;q=0.46, da-dk;q=0.42, da;q=0.38, fi-fi;q=0.35, fi;q=0.31"),
                                   ("Content-Type", "application/x-www-form-urlencoded"),
                                   ("Content-Length", "36") ]),


                BrowserPersonality("Explorer/ OSX",[
                                   ("Host", "192.168.5.2:8000"),
                                   ("Accept", "*/*"),
                                   ("Accept-Language", "en"),
                                   ("Pragma", "no-cache"),
                                   ("Connection", "Keep-Alive"),
                                   ("Referer", "http://192.168.5.2:8000/"),
                                   ("User-Agent", "Mozilla/4.0 (compatible; MSIE 5.23; Mac_PowerPC)"),
                                   ("UA-OS", "MacOS"),
                                   ("UA-CPU", "PPC"),
                                   ("Content-type", "application/x-www-form-urlencoded"),
                                   ("Extension", "Security/Remote-Passphrase"),
                                   ("Content-length", "36") ])
              ]

def getRandomPersonality():
  return random.choice(all_browsers)

### Main

#b = getRandomPersonality()
#print b.name + " " + str(b.getHeaders("localhost"))



import httplib

class MyHTTPConnection(httplib.HTTPConnection):
 def putrequest(self, method, url, skip_host=0, skip_accept=0):
       """Send a request to the server.

       `method' specifies an HTTP request method, e.g. 'GET'.
       `url' specifies the object being requested, e.g. '/index.html'.
       """

       # if a prior response has been completed, then forget about it.
       if self._HTTPConnection__response and self._HTTPConnection__response.isclosed():
           self._HTTPConnection__response = None

       #
       # in certain cases, we cannot issue another request on this connection.
       # this occurs when:
       #   1) we are in the process of sending a request.   (_CS_REQ_STARTED)
       #   2) a response to a previous request has signalled that it is going
       #      to close the connection upon completion.
       #   3) the headers for the previous response have not been read, thus
       #      we cannot determine whether point (2) is true.   (_CS_REQ_SENT)
       #
       # if there is no prior response, then we can request at will.
       #
       # if point (2) is true, then we will have passed the socket to the
       # response (effectively meaning, "there is no prior response"), and
       # will open a new one when a new request is made.
       #
       # Note: if a prior response exists, then we *can* start a new request.
       #       We are not allowed to begin fetching the response to this new
       #       request, however, until that prior response is complete.
       #
       if self._HTTPConnection__state == httplib._CS_IDLE:
           self._HTTPConnection__state = httplib._CS_REQ_STARTED
       else:
           raise CannotSendRequest()

       # Save the method we use, we need it later in the response phase
       self._method = method
       if not url:
           url = '/'
       str = '%s %s %s' % (method, url, self._http_vsn_str)

       self._output(str)

       if self._http_vsn == 11:
           # Issue some standard headers for better HTTP/1.1 compliance

           if not skip_host:
               # this header is issued *only* for HTTP/1.1
               # connections. more specifically, this means it is
               # only issued when the client uses the new
               # HTTPConnection() class. backwards-compat clients
               # will be using HTTP/1.0 and those clients may be
               # issuing this header themselves. we should NOT issue
               # it twice; some web servers (such as Apache) barf
               # when they see two Host: headers

               # If we need a non-standard port,include it in the
               # header.  If the request is going through a proxy,
               # but the host of the actual URL, not the host of the
               # proxy.

               netloc = ''
               if url.startswith('http'):
                   nil, netloc, nil, nil, nil = urlsplit(url)

               if netloc:
                   self.putheader('Host', netloc.encode("idna"))
               elif self.port == HTTP_PORT:
                   self.putheader('Host', self.host.encode("idna"))
               else:
                   self.putheader('Host', "%s:%s" % (self.host.encode("idna"), self.port))

           # note: we are assuming that clients will not attempt to set these
           #       headers since *this* library must deal with the
           #       consequences. this also means that when the supporting
           #       libraries are updated to recognize other forms, then this
           #       code should be changed (removed or updated).

           # we only want a Content-Encoding of "identity" since we don't
           # support encodings such as x-gzip or x-deflate.
           if skip_accept == 0:
              self.putheader('Accept-Encoding', 'identity')

           # we can accept "chunked" Transfer-Encodings, but no others
           # NOTE: no TE header implies *only* "chunked"
           #self.putheader('TE', 'chunked')

           # if TE is supplied in the header, then it must appear in a
           # Connection header.
           #self.putheader('Connection', 'TE')

       else:
           # For HTTP/1.0, the server will assume "not chunked"
           pass







class MyHTTPSConnection(httplib.HTTPSConnection):
 def putrequest(self, method, url, skip_host=0, skip_accept=0):
       """Send a request to the server.

       `method' specifies an HTTP request method, e.g. 'GET'.
       `url' specifies the object being requested, e.g. '/index.html'.
       """

       # if a prior response has been completed, then forget about it.
       if self._HTTPConnection__response and self._HTTPConnection__response.isclosed():
           self._HTTPConnection__response = None

       #
       # in certain cases, we cannot issue another request on this connection.
       # this occurs when:
       #   1) we are in the process of sending a request.   (_CS_REQ_STARTED)
       #   2) a response to a previous request has signalled that it is going
       #      to close the connection upon completion.
       #   3) the headers for the previous response have not been read, thus
       #      we cannot determine whether point (2) is true.   (_CS_REQ_SENT)
       #
       # if there is no prior response, then we can request at will.
       #
       # if point (2) is true, then we will have passed the socket to the
       # response (effectively meaning, "there is no prior response"), and
       # will open a new one when a new request is made.
       #
       # Note: if a prior response exists, then we *can* start a new request.
       #       We are not allowed to begin fetching the response to this new
       #       request, however, until that prior response is complete.
       #
       if self._HTTPConnection__state == httplib._CS_IDLE:
           self._HTTPConnection__state = httplib._CS_REQ_STARTED
       else:
           raise CannotSendRequest()

       # Save the method we use, we need it later in the response phase
       self._method = method
       if not url:
           url = '/'
       str = '%s %s %s' % (method, url, self._http_vsn_str)

       self._output(str)

       if self._http_vsn == 11:
           # Issue some standard headers for better HTTP/1.1 compliance

           if not skip_host:
               # this header is issued *only* for HTTP/1.1
               # connections. more specifically, this means it is
               # only issued when the client uses the new
               # HTTPConnection() class. backwards-compat clients
               # will be using HTTP/1.0 and those clients may be
               # issuing this header themselves. we should NOT issue
               # it twice; some web servers (such as Apache) barf
               # when they see two Host: headers

               # If we need a non-standard port,include it in the
               # header.  If the request is going through a proxy,
               # but the host of the actual URL, not the host of the
               # proxy.

               netloc = ''
               if url.startswith('http'):
                   nil, netloc, nil, nil, nil = urlsplit(url)

               if netloc:
                   self.putheader('Host', netloc.encode("idna"))
               elif self.port == HTTP_PORT:
                   self.putheader('Host', self.host.encode("idna"))
               else:
                   self.putheader('Host', "%s:%s" % (self.host.encode("idna"), self.port))

           # note: we are assuming that clients will not attempt to set these
           #       headers since *this* library must deal with the
           #       consequences. this also means that when the supporting
           #       libraries are updated to recognize other forms, then this
           #       code should be changed (removed or updated).

           # we only want a Content-Encoding of "identity" since we don't
           # support encodings such as x-gzip or x-deflate.
           if skip_accept == 0:
              self.putheader('Accept-Encoding', 'identity')

           # we can accept "chunked" Transfer-Encodings, but no others
           # NOTE: no TE header implies *only* "chunked"
           #self.putheader('TE', 'chunked')

           # if TE is supplied in the header, then it must appear in a
           # Connection header.
           #self.putheader('Connection', 'TE')

       else:
           # For HTTP/1.0, the server will assume "not chunked"
           pass


#!/usr/bin/python

import browserpersonality
import myhttp

import HTMLParser
import urlparse
import urllib
import httplib
import re
import zlib
import types
import string
import random

##  TODO : http-equiv redirect
##  Ignore html comments (OK)
##  Ignore empty attrs <font size=>
##  Add POST data Content-Type: multipart/form-data
##      -open: when data is given it assumes: application/x-www-form-urlencoded
##             browser personality also assumes this
##      -basic hack when seen in forms

# Submit
# Cookie: PREF=ID=778645db55232677:FF=4:LD=en:NR=10:TM=1049334649:LM=1093300410:C2COFF=1:L=0qY1RAA:S=GD2wOY2awbdRoMVp; 4=; PREF=ID=778645db55232677:TM=1049334649:LM=1083289959:L=0qY1RAA:S=4OCnhW_GzPkicKYd

# Set:
# set-cookie: PREF=ID=2ea55dba094190c2:TM=1101256797:LM=1101256797:S=Jswm6aHL_KcrTKTZ; expires=Sun, 17-Jan-2038 19:14:07 GMT; path=/; domain=.google.com
# [set-cookie] [ASPSESSIONIDCAQQQCDC=KMOHHBIDAEHMILFGKDKMLEOD; path=/]


def decomment(html):
  ret = ""
  p1 = 0
  p2 = html.find("<!--",p1)
  while p2 != -1:
     if p2 != p1:
        ret += html[p1:p2]
     p1 = html.find("-->", p2)
     if p1 == -1:
        break
     p1 += 3
     p2 = html.find("<!--",p1)
  ret += html[p1:]
  return ret

"""
rfc 2046
boundary := 0*69<bchars> bcharsnospace

bchars := bcharsnospace / " "

bcharsnospace := DIGIT / ALPHA / "'" / "(" / ")" /
                 "+" / "_" / "," / "-" / "." /
                 "/" / ":" / "=" / "?"

"""
boundaryLowerBound = 28
boundaryUpperBound = 36
boundaryAlphabet = string.ascii_letters + string.digits

def getBoundaryString( ):
  dashCount = random.randrange( boundaryLowerBound, boundaryUpperBound + 1 )
  charCount = random.randrange( boundaryLowerBound, boundaryUpperBound + 1 )
  boundaryString = '-' * dashCount
  boundaryString += "".join( [ random.choice( boundaryAlphabet ) for i in range( 0, charCount ) ] )
  return boundaryString


class Cookie:
  def __init__(self, domain, path, exp, value):
     self.domain = domain
     self.path = path
     self.exp = exp
     self.value = value

  def getClientHeader(self):
     return self.value


class Form:
  def __init__(self, browser, method, action, name, enctype):
     self.browser = browser
     self.method = method
     self.action = action
     self.name = name
     self.enctype = enctype
     self.fieldorder = []
     self.radios = {}
     self.fields = {}
     self.buttons = {}

  def addField(self, name, value):
     self.fields[name] = value
     self.fieldorder.append(name)

  def addRadio(self, name, value,checked):
     self.radios[(name,value)] = checked
     self.fieldorder.append((name,value))

  def checkRadio(self, name, value, checked=1):
     self.radios[(name,value)] = checked

  """
  def encode_multipart_formdata(fields, files):

     fields is a sequence of (name, value) elements for regular form fields.
     files is a sequence of (name, filename, value) elements for data to be uploaded as files
     Return (content_type, body) ready for httplib.HTTP instance

     BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
     CRLF = '\r\n'
     L = []
     for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
     for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
     L.append('--' + BOUNDARY + '--')
     L.append('')
     body = CRLF.join(L)
     content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
     return content_type, body
  """

  def getMultiPartData( self, ordered ):
     boundaryString = getBoundaryString( )
     crlf = '\r\n'
     messageBody = []
     for ( fieldName, fieldVal ) in ordered:
        messageBody.append( "--" + boundaryString + crlf )
        messageBody.append( 'Content-Disposition: form-data; name="%s"' % ( fieldName ) )
        messageBody.append( crlf * 2 )
        messageBody.append( fieldVal )
        messageBody.append( crlf )

     messageBody.append( "--" + boundaryString + "--" + crlf )
     messageBody = "".join( messageBody )
     return ( boundaryString, messageBody )

  def encode(self, buttonname):
     ordered = []
     for f in self.fieldorder:
        if type(f) == types.TupleType:
           if self.radios[f] == 1:
              ordered.append(f)
        else:
           ordered.append((f,self.fields[f]))

     #TODO: should this encode the button somehow??
     #      other encoding types?
     if self.enctype == "multipart/form-data":
        return self.getMultiPartData( ordered )

     ret = urllib.urlencode(ordered)

     if not buttonname:
        return  ret
     else:
        button = {}
        if buttonname in self.buttons:
           button[buttonname] = self.buttons[buttonname]
        else:
           button[buttonname] = ""
        ret =  ret
        if len(ret) != 0:
           ret += "&"
        return  ret + urllib.urlencode(button)

  def click(self, buttonname):
     if self.method == "post":
        return self.browser.doPost(self.action, self.encode(buttonname))
     return self.browser.doGet(self.action, self.encode(buttonname))


class BrowserParser(HTMLParser.HTMLParser):
  def __init__(self, browser):
     HTMLParser.HTMLParser.__init__(self)
     self.browser = browser
     self.links = []
     self.forms = []
     self.currentForm = None

  def handle_starttag(self, tag, attrs):
     if tag == "a":
        self.proc_link(attrs)
     elif tag == "form":
        self.proc_form(attrs)
     elif tag == "input":
        self.proc_input(attrs)
     elif tag == "textarea":
        self.proc_textarea(attrs)

  def handle_endtag(self, tag):
     if tag == "form":
        self.forms.append(self.currentForm)
        self.currentForm = None
     return

  def handle_data(self, data):
     return

  def proc_form(self, attrs):
     method = ""
     action = ""
     name = ""
     enctype = ""
     for (key, val) in attrs:
        if key == "method":
           method = val
        elif key == "action":
           action = val
        elif key == "name":
           name = val
        elif key == "enctype":
           enctype = val
     self.currentForm = Form(self.browser, method, action, name, enctype)

  def proc_textarea(self, attrs):
     name = ""
     value = ""
     for (key, val) in attrs:
        if key == "name":
           name = val
     self.currentForm.addField(name, value)

  def proc_input(self, attrs):
     name = ""
     value = ""
     type = ""
     checked = 0
     for (key, val) in attrs:
        if key == "name":
           name = val
        elif key == "value":
           value = val
        elif key == "type":
           type = val
        elif key == "checked":
           checked = 1

     if name != "":
        if type == "submit":
           self.currentForm.buttons[name] = value
        elif type == "checkbox":
           self.currentForm.addRadio(name,value,checked)
        elif type != "reset":
           self.currentForm.addField(name, value)


  def proc_link(self, attrs):
     for (key, val) in attrs:
        if key == "href":
           self.links.append(val)


#uchar [a-zA-Z0-9$\-_\.\+\!\*'\(\),]

netpat = "([a-zA-Z0-9\-\.]+)(:[0-9]+)?"
pathpat = "([a-zA-Z0-9$\-_\.\+\~\!\*'\(\),/]*/)([a-zA-Z0-9$\-_\.\+\!\*'\(\),]+)?"

class Browser:
  def __init__(self, url, personality = None, referer = None, cookies = None, debug = None):
     self.personality = personality
     self.debug = debug
     self.referer = referer

     (scheme, net, path, params, query, frag) = urlparse.urlparse(url)
     self.protocol = scheme

     res = re.match(netpat, net)
     if not res:
        raise Exception("Illegal network part in: " + url)
     self.host = res.group(1);
     if res.group(2):
        self.port = int(res.group(2)[1:])
     else:
        if self.protocol == "https":
           self.port = 443
        else:
           self.port = 80

     if self.debug:
        print "Proto [%s] host [%s] port [%i]" % (self.protocol, self.host, self.port)

     self.documentroot = "/"
     self.filename = ""
     #print "Pathmatch: " + path
     if path != "":
        res = re.match(pathpat, path)
        if not res:
            raise Exception("Illegal path part in: " + url)
        if self.debug:
           print "[%s] [%s] [%s]" % (res.group(0), res.group(1), res.group(2))
        if res.group(1):
           self.documentroot =  res.group(1)
        if res.group(2):
           self.filename = res.group(2)
     if self.debug:
        print "Root [%s] file [%s]" % (self.documentroot, self.filename)

     self.query = query

     self.headers = []
     self.page = ""
     self.status = 0
     self.links = []
     self.forms = []

     if cookies:
        self.cookies = [] + cookies
     else:
        self.cookies = []


  def open(self, data=None):
     if self.protocol == "https":
        conn = myhttp.MyHTTPSConnection(self.host, self.port)
     else:
        conn = myhttp.MyHTTPConnection(self.host, self.port)
     conn.connect()

     req = self.documentroot + self.filename
     if self.query:
        req += "?" + self.query
     if self.debug:
        print "Retrieving " + req

     hostpart = self.host
     if self.protocol == "https" and self.port != 443:
        hostpart += ":" + str(self.port)
     elif self.protocol == "http" and self.port != 80:
        hostpart += ":" + str(self.port)

     if data:
        isMultiPart = 0
        if type( data ) == types.TupleType:
           isMultiPart = 1
        conn.putrequest("POST", req, skip_host=1, skip_accept=1)
        if self.personality:
           if isMultiPart:
              headers = self.personality.getHeaders(hostpart, self.referer, len(data[1]))
           else:
              headers = self.personality.getHeaders(hostpart, self.referer, len(data))
           for (key,val) in headers:
              if key == "Content-Type" and isMultiPart:
                 conn.putheader( key, 'multipart/form-data; boundary=%s' % data[0] )
                 continue
              conn.putheader(key, val)
        else:
           conn.putheader("Host", hostpart)
           if isMultiPart:
              conn.putheader( "Content-Type", 'multipart/form-data; boundary=%s' % data[0] )
              conn.putheader("Content-Length", str(len(data[1])))
           else:
              conn.putheader("Content-Type", "application/x-www-form-urlencoded")
              conn.putheader("Content-Length", str(len(data)))
        if len(self.cookies) > 0:
           conn.putheader("Cookie",  self.cookies[0].getClientHeader())
           if self.debug:
              print "Putting cookie: " + self.cookies[0].getClientHeader()
        conn.endheaders()
        if self.debug:
           print "Putting data: " + str( data )
        if isMultiPart:
           conn.send(data[1])
        else:
           conn.send(data)
     else:
        conn.putrequest("GET", req, skip_host=1, skip_accept=1)
        if self.personality:
           headers = self.personality.getHeaders(hostpart, self.referer, 0)
           for (key,val) in headers:
              conn.putheader(key, val)
        else:
           conn.putheader("Host", hostpart)
        if len(self.cookies) > 0:
           conn.putheader("Cookie",  self.cookies[0].getClientHeader())
        conn.endheaders()
     response = conn.getresponse()
     self.page = response.read()
     self.status = response.status
     self.headers = response.msg.items()


     if "set-cookie" in response.msg:
        self.processCookie(response.msg["set-cookie"])

     if "content-encoding" in response.msg:
        enctype = response.msg["content-encoding"]
        if enctype == "gzip" or enctype == "x-gzip":

           self.page = zlib.decompress(self.page)
           print "Decompressed: " + self.page
        elif enctype != "identity":
           print "Error: Got data encoded in an unknown way! (" + enctype + ")"


  def processCookie(self, cookie):
     toks = cookie.split(";")
     if self.debug:
           print "Got cookie: " + toks[0]
     c = Cookie(None, None, None, toks[0])
     self.cookies.append(c)

  def parse(self):
     p = BrowserParser(self)
     p.feed(decomment(self.page))
     p.close()
     self.links = p.links
     self.forms = p.forms

  def getHeader(self, key):
     for  (tkey, val) in self.headers:
        if key == tkey:
           return val
     return None

  def isRedirect(self):
     if self.status == 302 or self.status == 301:
        return 1
     else:
        return None

  def doRedirect(self):
     if not self.isRedirect():
        return None
     else:
        loc = self.getHeader("location")
        if self.debug:
           print "New location is " + loc
        ret = Browser(self.getFullLink(loc), self.personality, self.getFullLink(self.filename), self.cookies, self.debug)
        ret.open()
        return ret

  def doRedirects(self):
     ptr = self
     while ptr.isRedirect():
        ptr = ptr.doRedirect()
     return ptr

  def getFullLink(self, link):
     if link == "":
        link = "/"

     if link.find("://") != -1:
        return link
     elif link[0] == '/':
        ret = self.protocol + "://" + self.host
        if self.protocol == "https" and self.port != 443:
           ret += ":" + str(self.port)
        elif self.protocol == "http" and self.port != 80:
           ret += ":" + str(self.port)
        ret += link
        return ret
     else:
        ret = self.protocol + "://" + self.host
        if self.protocol == "https" and self.port != 443:
           ret += ":" + str(self.port)
        elif self.protocol == "http" and self.port != 80:
           ret += ":" + str(self.port)
        ret += self.documentroot + link
        return ret

  def containsLink(self, link):
     tst = self.getFullLink(link)
     for l in self.links:
        if tst == self.getFullLink(l):
           return 1
     return None

  def containsLinks(self, links):
     for l in links:
        if not self.containsLink(l):
           return None
     return 1

  def click(self, link):
     full = self.getFullLink(link)
     page = Browser(full, self.personality, self.getFullLink(self.filename), self.cookies, self.debug)
     page.open()
     return page

  def doPost(self, link, data):
     full = self.getFullLink(link)
     (scheme, net, path, params, query, frag) = urlparse.urlparse(full)
     full =  urlparse.urlunparse((scheme, net, path, params, "", ""))
     page = Browser(full, self.personality, self.getFullLink(self.filename), self.cookies, self.debug)
     page.open(data)
     return page

  def doGet(self, link, data):
     full = self.getFullLink(link)
     #print "Opening " + full
     (scheme, net, path, params, query, frag) = urlparse.urlparse(full)
     query = data
     #print "With data " + urlparse.urlunparse((scheme, net, path, params, query, frag))
     page = Browser( urlparse.urlunparse((scheme, net, path, params, query, frag)), self.personality, self.getFullLink(self.filename), self.cookies, self.debug)
     page.open()
     return page

  def printInfo(self):
     print "Headers:"
     for (key, val) in self.headers:
        print "[%s] [%s]" % (key, val)

     print "Links:"
     for l in self.links:
        print "Link: " + l

     print "Forms:"
     for f in self.forms:
        print "Form %s: %s %s" % (f.name, f.action, f.encode(None))

     print "Cookies:"
     for c in self.cookies:
         print "Cookie: %s" % c.getClientHeader()

