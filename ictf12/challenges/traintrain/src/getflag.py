import mechanize
import sys
import re

class GetFlag():
    baseurl = ""
    error = 0
    error_msg = ''
    flag = ''
    browser = None
    
    def execute(self, ip, port, flag_id, cookie):

        # flag_id is the account 
        # cookie is the password
        self.baseurl = "http://%s:%s" % (str(ip), str(port))
        
        try:
            self.browser = mechanize.Browser()
            page = self.browser.open("%s/" % self.baseurl)
            contents = page.read()
            
            if not "Welcome to the Train Transportation Training" in contents:
                self.error = 1
                self.error_msg= "Login page non-functional"
                return
            #print "Checking the forms..."
            #forms = self.browser.forms()
            #for form in forms:
            #    print form
            self.browser.select_form(name="login")
            self.browser["username"] = flag_id
            self.browser["password"] = cookie
            response = self.browser.submit()
            contents = response.read()
            if "your authorization data" in contents:
                search = re.search("your authorization data is:</p>[\s\n]*<pre>[\s\n]*(.*)[\s\n]*</pre>", contents)
                self.flag = search.group(1)
                self.flag = self.flag.strip()
                return
            elif "Authentication failed" in contents:
                self.flag = ""
                self.error = 1
                self.error_msg = "Login credentials are incorrect"
                return
            else:
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
        print "Starting to retrieve flag for traintrain..."
        b = GetFlag()
        b.execute(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        print "Finished executing"
        print b.result()
    except Exception, e:
        print "Error: %s" % str(e)
    