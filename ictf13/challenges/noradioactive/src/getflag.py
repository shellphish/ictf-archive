import mechanize
import sys
import re

class GetFlag():
    baseurl = ""
    error = 0
    error_msg = ''
    flag = ''
    browser = None
    
    def execute(self, ip, port, flag_id, token):

        # flag_id is the account 
        # token is the password
        self.baseurl = "http://%s:%s" % (str(ip), str(port))
        self.error = 0
        self.error_msg = "OK"
        
        try:
            self.browser = mechanize.Browser()
            page = self.browser.open("%s/" % self.baseurl)
            contents = page.read()
            
            if not "Mfumo Wa Mionzi Ya Kufuatilia" in contents:
                self.error = 1
                self.error_msg= "Login page non-functional"
                return
            #print "Checking the forms..."
            #forms = self.browser.forms()
            #for form in forms:
            #    print form
            self.browser.select_form(name="login")
            self.browser["username"] = flag_id
            self.browser["password"] = token
            response = self.browser.submit()
            contents = response.read()
            if "Tafadhali kuwasilisha mpya mionzi kusoma" in contents:
                search = re.search("\[Idadi: (.*)\]", contents)
                self.flag = search.group(1)
                self.flag = self.flag.strip()
                return
            elif "Kosa ilitokea wakati usindikaji kuingia yako" in contents:
                self.flag = ""
                self.error = 1
                self.error_msg = "Login credentials are incorrect"
                return
            else:
                print "Flag retrieveal failed: %s" % contents
                self.flag = ""
                self.error = 1
                self.error_msg = "Flag retrieval failed" 
                return
        except Exception, e:
            self.flag = ""
            self.error = 1
            self.error_msg = "Flag fetching exception: %s" % str(e)
            return 
        
        return 
            
    def result(self):
        return {'FLAG' : self.flag,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }
        
        
if __name__== "__main__":
    try:
        print "Starting to retrieve flag for noradioactive..."
        b = GetFlag()
        b.execute(sys.argv[1], 9292, sys.argv[2], sys.argv[3])
        print "Finished executing"
        print b.result()
    except Exception, e:
        print "Error: %s" % str(e)
    
