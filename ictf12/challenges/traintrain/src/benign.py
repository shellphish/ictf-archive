import mechanize
import sys
import random
import time

consonants = [
    ('b',  2),
    ('c',  2),
    ('ch', 1),
    ('d',  4),
    ('f',  2),
    ('g',  3),
    ('h',  2),
    ('j',  1),
    ('k',  1),
    ('l',  4),
    ('m',  2),
    ('n',  6),
    ('p',  2),
    ('q',  1),
    ('qu', 1),
    ('r',  6),
    ('s',  4),
    ('t',  6),
    ('v',  2),
    ('w',  2),
    ('x',  1),
    ('z',  1),
]

vowels = [
    ('a', 9),
    ('e', 12),
    ('i', 9),
    ('o', 8),
    ('u', 4),
    ('y', 2),
]

def selection(table):

    # sum the table if needed

    if type(table[-1]) is not type(0):
        s = 0
        for i in range(len(table)):
            s += table[i][1]
        table.append(s)
    else:
        s = table[-1]

    # now the selection
    n = random.randrange(s) + 1
    for i in range(len(table)-1):
        n -= table[i][1]
        if n <= 0:
            return table[i][0]

    # should not happen
    return ''

def generate(minsyl = 1, maxsyl = 3):

    numsyl = random.randint(minsyl, maxsyl)

    word = []

    for i in range(numsyl):
        flag = 0
        if random.randrange(100) < 60:
            word.append(selection(consonants))
            flag = 1
        word.append(selection(vowels))
        if not flag or random.randrange(100) < 40:
            word.append(selection(consonants))

    return "".join(word)


class Benign():
    error = 0
    error_msg = "OK"
    logged_in = False
    baseurl = ""
    browser = None
    
    def generate_solution(self):
        return "3"
    
    def generate_username(self):
        print "Generating username"
        return generate(2, 8)
    
    def generate_password(self):
        print "Generating password"
        return generate(6, 10)
    
    def generate_authorization(self):
        authorization = ""
        for i in range(32):
            c = random.choice('abcde0123456789')
            authorization = authorization + c
        return authorization
        
    def register(self):
        print "Starting to register..."
        try:
            page = self.browser.open("%s/" % self.baseurl)
            contents = page.read()
            if not "Welcome to the Train Transportation Training" in contents:
                self.error = 1
                self.error_msg= "Register page non-functional"
                return None
            print "Checking the forms..."
            forms = self.browser.forms()
            for form in forms:
                print form
            self.browser.select_form(name="register")
            print "Generating names/passes"
            username = self.generate_username()
            password = self.generate_password()
            authorization = self.generate_authorization()
            print "Chosen u:%s p:%s a:%s" % (username, password, authorization)
            self.browser["username"] = username
            self.browser["password"] = password
            self.browser["authorization"] = authorization
            
            response = self.browser.submit()
            contents = response.read()
            if "User successfully registered" in contents:
                print "Registration successful!"
                return (username, password)
            else:
                print "Registration failed: [%s]" % contents
                raise
        except Exception, e:
            self.error = 1
            self.error_msg("Registration page exception: %s" % str(e))
        return None
        
    def login(self, username, password, correct=True):
        print "Starting to log in..."
        try:
            page = self.browser.open("%s/" % self.baseurl)
            contents = page.read()
            if not "Welcome to the Train Transportation Training" in contents:
                self.error = 1
                self.error_msg= "Login page non-functional"
                return 1
            print "Checking the forms..."
            forms = self.browser.forms()
            for form in forms:
                print form
            self.browser.select_form(name="login")
            self.browser["username"] = username
            self.browser["password"] = password
            response = self.browser.submit()
            contents = response.read()
            if "your authorization data" in contents:
                print "Login successful!"
                return 0
            elif "Authentication failed" in contents and correct == False:
                print "Login correctly unsuccessful (this was supposed to happen)!"
                return 0
            else:
                print "Login failed: [%s]" % contents
                raise
        except Exception, e:
            self.error = 1
            self.error_msg("Login page exception: %s" % str(e))
            return 1
        return 0
    
    def logout(self):
        print "Logging out..."
        page = self.browser.open("%s/logout" % self.baseurl)
        contents = page.read()
        if "You have been logged out" in contents:
            print "Successfully logged out!"
            self.logged_in = False
            return 0
        elif "You are not logged in" in contents:
            print "I was already logged out!"
            self.logged_in = False
            return 0
        else:
            self.error = 1
            self.error_msg = "Logout page non-functional"
            print "This is not the logout page: [%s]" % contents
            
        return 1
        
    def sleep_random(self, min_secs=1, max_secs=4):
        timeout_range = int(abs(max_secs-min_secs))
        timeout = random.choice(range(timeout_range))
        print "Sleeping for %d seconds" % (timeout)
        time.sleep(timeout)
        return
    
    def manual(self):
        print "Reading the manual..."
        url = "%s/manual" % self.baseurl
        print "Opening URL %s" % url
        page = self.browser.open(url)
        contents = page.read()
        if not "documentation" in contents:
            print "This is not the manual: %s" % contents
            self.error = 1
            self.error_msg = "Manual page non-functional"
            return 1
        print "The manual is working ok!"
        return 0
    
    def assignment(self):
        print "Starting to work on my assignment"
        try:
            page = self.browser.open("%s/" % self.baseurl)
            contents = page.read()
            if not "Please submit the solution to your training assignment for scoring" in contents:
                print "This is the wrong assignment page: [%s]" % contents
                self.error = 1
                self.error_msg = "Assignment page non-functional"
                return 1
            print "Setting the link..."
            for link in self.browser.links():
                if "assignment" in link.url:
                    break
            
            print "Following link: %s" % str(link)
            self.browser.follow_link(link)
            print "Link followed"
            page = self.browser.open("%s/" % self.baseurl)
            
            self.browser.select_form("solution")
            self.browser["solution"] = self.generate_solution()
            
            response = self.browser.submit()
            print "Form submitted"
            contents = response.read()
            if not "Your solution is" in contents:
                raise
            print "Assignment completed (right or wrong, does not matter)"
        except Exception, e:
            self.error = 1
            self.error_msg = "Assignment page non-functional: %s" % str(e)
            return 1
        
        return 0
        
    def execute(self, ip, port):
        self.error = -1
        self.error_msg = "Connection failed"
        print "Connecting to home page"
        try:
            self.browser = mechanize.Browser()
            self.baseurl = "http://%s:%s" % (str(ip), str(port))
            page = self.browser.open(self.baseurl)
            print page.read()
        except Exception, e:
            self.error = -1
            self.error_msg = "Connection failed"
            return
        self.error = 0
        self.error_msg = "OK"
        try:
            max_iterations = 10
            iterations = 2 + random.choice(range(max_iterations))
            print "DOING %d ITERATIONS..." % iterations
            for i in range(iterations):
                print "Doing iteration %d out of %d" % (i, iterations)
                self.sleep_random()
                choice = random.choice(('register', 'login', 'manual','logout'))
                #choice = 'logout'
                print "Choosing to do: %s..." % choice
                if choice == 'login':
                    if self.logout(): return
                    self.sleep_random()
                    username = self.generate_username()
                    password = self.generate_password()
                    if self.login(username, password, False): return
                elif choice == 'register':
                    if self.logout(): return
                    self.sleep_random() 
                    res = self.register()
                    if res == None: return
                    username = res[0]
                    password = res[1]
                    next = random.choice(('login', 'back'))
                    #next = 'login'
                    if next == 'back':
                        print "After registration, I am going back..."
                        continue
                    self.sleep_random()
                    print "Logging in with the username and password that I just registered"
                    if self.login(username, password): return
                    self.sleep_random()
                    print "Doing my assignment..."
                    if self.assignment(): return
                    continue
                elif choice == 'manual':
                    if self.manual(): return
                elif choice == 'logout':
                    if self.logout(): return
                else:
                    self.error = 1
                    self.error_msg = "Unknown choice: %s" % choice
                    return
        except Exception, e:
            self.error = -1
            self.error_msg = "Benign behavior failed: %s" % str(e)
            return 1
        self.error = 0
        self.error_msg = "OK"
        return 0
        
    def result(self):
        return {'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }

if __name__== "__main__":
    try:
        print "Starting benign traintrain..."
        b = Benign()
        b.execute(sys.argv[1], sys.argv[2])
        print b.result()
    except Exception, e:
        print "Error: %s" % str(e)
    
    