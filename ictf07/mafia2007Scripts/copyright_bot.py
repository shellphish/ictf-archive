#!/usr/bin/python

"""
http://<server>/~copyright/cgi-bin/account.php

COOKIE is <email>:<password>
(POST)

first=<flag>&email=<email>&password=<password>

This stores a new flag under ID <email>

http://<server>/~copyright/cgi-bin/login.php
(POST)
email=<email>&password=<password>

This logs in and creates the cookie

http://<server>/~copyright/cgi-bin/upload.php
This stores a new file (functionality check only)

http://<server>/~copyright/cgi-bin/star.php
This returns the flag as the first name in the Hello line

"""


import os, random, time, sys, string, re, socket, urllib
import httplib

import ImageScripts.BaseScoringScript as scoringScript
from ImageScripts.Utility import pybrowse, browserpersonality

def execution_path(filename):
    return os.path.join(os.path.dirname(sys._getframe(1).f_code.co_filename), filename)

class copyrightScoringScript(scoringScript.BaseScoringScript):
    
    def post_multipart(self,host, selector, fields, files, cookie):
       content_type, body = self.encode_multipart_formdata(fields, files)
       h = httplib.HTTPConnection(host)  
       headers = {
           'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686;) Firefox/2.0.0.6',
           'Cookie': cookie,
           'Content-Type': content_type
           }
       h.request('POST', selector, body, headers)
       res = h.getresponse()
       return res.status, res.reason, res.read()    
    
    
    def encode_multipart_formdata(self,fields, files):
       """
       fields is a sequence of (name, value) elements for regular form fields.
       files is a sequence of (name, filename, value) elements for data to be uploaded as files
       Return (content_type, body) ready for httplib.HTTP instance
       """
       BOUNDARY = '----------8506126151759583858729434387'
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
           L.append('Content-Type: %s' % self.get_content_type(filename))
           L.append('')
           L.append(value)
       L.append('--' + BOUNDARY + '--')
       L.append('')
       body = CRLF.join(L)
       content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
       return content_type, body
    
    def get_content_type(self,filename):
       #return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
       return 'application/octet-stream'
     
    def getRandomSentence(self,len):
        ret = ""
        for i in range(len):
            ret += self.getRandomString(random.randint(1,8)) + " "
        return ret
     
    def doScoring(self):
        # get old flag
        oldFlag = ""
        if self.cookie != None:
            (myemail, mypassword) = self.cookie.split(':');
            try:
                personality = browserpersonality.getRandomPersonality()
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site/Sound_of_music.html")
                mainpg.open()
                # Logs in
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site/Sound_of_music_files/widget2_markup.html")
                mainpg.open()
                mainpg.parse()
    
                qForm = mainpg.forms[0]
                qForm.fields["email"] = myemail 
                qForm.fields["password"] = mypassword
                
                resultingPage = qForm.click( None )
                resultingPage = resultingPage.doRedirects( )
    
                successPtr = resultingPage.page.find("successfully authenticated")
                if successPtr == -1:
                    oldFlag = ""
                else:
                    mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site/Sound_of_music.html")
                    mainpg.open()
                    mainpg.parse()
                    resultingPage = pybrowse.Browser("http://" + self.teamIp + "/~copyright/cgi-bin/star.php", resultingPage.personality, resultingPage.referer, resultingPage.cookies)

                    resultingPage.open()
                    resultingPage.parse()
                    successPtr = resultingPage.page.find("Hello ")
                    if successPtr != -1:
                        oldFlag = resultingPage.page[successPtr+6:][:self.getFlagSize()]
                    else:
                        oldFlag = ""
                    
                
                self.validatePreviousFlag(oldFlag)

            except Exception, e:
                self.output.write("got exception [%s] getting flag" % (e))
                sys.exit(1)
                
        
        # set the new flag
        try:
            personality = browserpersonality.getRandomPersonality()
            mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site/Sound_of_music.html")
            mainpg.open()
            mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site/Sound_of_music_files/widget1_markup.html")
            mainpg.open()
            mainpg.parse()

            qForm = mainpg.forms[0]
            myfirst = self.getNewFlagText()
            mylast = self.getRandomString(random.randint(3,10))
            myemail = self.getRandomEmail()
            mypassword = self.getRandomString(random.randint(3,10))
            
            qForm.fields["first"] = myfirst
            qForm.fields["last"] = mylast
            qForm.fields["email"] = myemail
            qForm.fields["password"] = mypassword
            
            self.cookie = qForm.fields["email"] + ":" + qForm.fields["password"]
            resultingPage = qForm.click(None)
            resultingPage = resultingPage.doRedirects()
            successPtr = resultingPage.page.find("successfully created")
            if successPtr == -1:
                self.returnVal.setError()
                return
        except Exception, e:
            self.output.write("got exception %s setting flag" % (e))
            self.returnVal.setError()
            return
            
        self.returnVal.setSuccess()
        return
    
    def exerciseService(self):
        if random.randint(1, 100) < 200 and self.cookie != None:
            try:
                (myemail, mypassword) = self.cookie.split(':');
                
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site/Sound_of_music.html")
                mainpg.open()
                # Logs in
                mainpg = pybrowse.Browser("http://" + self.teamIp + "/Site/Sound_of_music_files/widget2_markup.html")
                mainpg.open()
                mainpg.parse()

                qForm = mainpg.forms[0]
                qForm.fields["email"] = myemail 
                qForm.fields["password"] = mypassword 
                resultingPage = qForm.click( None )
                resultingPage = resultingPage.doRedirects( )
                successPtr = resultingPage.page.find("successfully authenticated")
                if successPtr == -1:
                    print "error service not functional: can't login in"
                    sys.exit(5)
                # uploads some music tune
                if random.randint(1, 10) < 20:
                    resultingPage = pybrowse.Browser("http://" + self.teamIp + "/Site/Sound_of_music.html", resultingPage.personality, resultingPage.referer, resultingPage.cookies)
                    resultingPage.open()
                    # uploads the file
                    resultingPage = pybrowse.Browser("http://" + self.teamIp + "/Sound_of_music_files/widget3_markup.html", resultingPage.personality, resultingPage.referer, resultingPage.cookies)
                    resultingPage.open()
                    resultingPage.parse()
                    #resultingPage.printInfo()
                    cookie = resultingPage.cookies[0].getClientHeader()
                    #print "Cookie: " + cookie
                    myfile = execution_path(self.getRandomString(random.randint(3,10)))
                    #qForm.fields["file"] = myfile
                    # creates the file
                    f = open(myfile, "w+")
                    content = self.getRandomString(random.randint(10,1000))
                    f.write(content)
                    f.close()
                    comment =self. getRandomSentence(random.randint(5,100))
                    command = "mp3info -f -c '" + comment + "' " + myfile 
                    os.system(command)
                    f = open(myfile, "r")
                    content = f.read()
                    f.close()
                    #print "Sending content: [" + content + "]"
                    status, reason, data = self.post_multipart(myHost, "/~copyright/cgi-bin/upload.php", [], [('file', myfile, content)], cookie)
                    #print data
                    successPtr = data.find("successfully received")
                    if successPtr == -1:
                        sys.exit(5)
            except Exception, e:
                sys.exit(6)

    
def getScoringScript():
    """
    this must be defined in every scoring module.
    """
    return copyrightScoringScript
