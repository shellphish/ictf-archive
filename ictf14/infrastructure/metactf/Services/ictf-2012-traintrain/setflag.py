import mechanize
import sys
import random

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


class SetFlag():
    flag_id = ""
    cookie = ""
    error = 0
    error_msg = "OK"
    
    def generate_username(self):
        return generate(2, 10)
    
    def generate_password(self):
        return generate(6, 10)
    
    def execute(self, ip, port, flag):

        self.baseurl = "http://%s:%s" % (str(ip), str(port))
        self.flag = str(flag)
        
        try:
            self.browser = mechanize.Browser()
            page = self.browser.open("%s/" % self.baseurl)
            contents = page.read()
            
            if not "please register using the form below" in contents:
                print "Problem [%s]" % contents
                self.error = 1
                self.error_msg= "Registration page not accessible"
                return
            self.browser.select_form(name="register")
            username = self.generate_username()
            password = self.generate_password()
            authorization = self.flag
            self.browser["username"] = username
            self.browser["password"] = password
            self.browser["authorization"] = authorization
            
            
            page = self.browser.submit()
            contents = page.read()
            if not "User successfully registered" in contents:
                self.error = 1
                self.error_msg = "Registration not functional"
                return
            self.flag_id = username
            self.cookie = password
            return
        except Exception, e:
            self.error = 1
            self.error_msg = "Flag setting exception: %s" % str(e)
            return 

    def result(self):
        return {'FLAG_ID' : self.flag_id,
                'TOKEN' : self.cookie,
                'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }

if __name__== "__main__":
    try:
        print "Starting to set flag for traintrain..."
        b = SetFlag()
        b.execute(sys.argv[1], sys.argv[2], sys.argv[3])
        print "Finished executing"
        print b.result()
    except Exception, e:
        print "Error: %s" % str(e)
