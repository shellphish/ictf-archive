import requests
import random
#from pip._vendor.html5lib.ihatexml import digit

def luhn_checksum(card_number):
    def digits_of(n):
        digit_list = list()
        for d in str(n):
            try:
                v = int(d)
            except:
                v = 0
            digit_list.append(0) 
        return digit_list
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10


def is_luhn_valid(card_number):
    return luhn_checksum(card_number) == 0
   
   
class SetFlag:

    nouns = (["A dude", "Your mom", "The king of swing", "Some guy", "A pangolin with rabies", "A sloth", "Your homie", "This cool guy my cousin met yesterday", "Wolverine"], ["These dudes", "Both of my moms", "All the kings of the world", "Some guys", "All of a cattery's cats", "The multitude of sloths living under your bed", "Your homies", "Like, these, like, all these people", "The X-Men"])
    verbs = (["eats", "kicks", "gives", "treats", "meets with", "creates", "hacks", "configures", "spies on", "thinks", "meows on", "flees from", "tries to automate", "explodes", "hacks"], ["eat", "kick", "give", "treat", "meet with", "create", "hack", "configure", "spy on", "retard", "meow on", "flee from", "try to automate", "explode"])
    infinitives = ["to make a pie.", "for no apparent reason.", "because the sky is green.", "for a disease.", "to be able to make toast explode.", "to know more about archeology.", "because it is so."]


    def generate_cc(self):
        cc = list()
        checksum = list()
        do_mul = 0
        for i in range(15):
            digit = random.randint(0, 9)
            cc.append(digit)
            if do_mul:
                checksum.append(digit * 2)
                do_mul = 0
            else:
                do_mul = 1
        sum = 0
        for digit in checksum:
            sum = sum + digit
        final_digit = sum % 10
        cc.append(final_digit)
        res = ""
        for digit in cc:
            res = res + str(digit)
        return res


    def generate_comment(self):
        number = random.randint(0,1)
        sub = "%s %s" % (random.choice(self.nouns[number]),
                         random.choice(self.verbs[number]))
        number = random.randint(0,1)
        obj = random.choice(self.nouns[number]).lower()

        reason = random.choice(self.infinitives)

        comment = "%s %s %s" % (sub, obj, reason)
        return comment
    

    def execute(self, ip, port, flag):
        self.token = self.generate_cc()
        self.flag_id = self.generate_comment() 
        self.error = 0
        self.error_msg = ''
        
        payload = {'candidate': random.choice(['Blitzkrieg','Stallone','Schtrappe','Schmidt','Blix']),
                   'cc': self.token,
                   'amount': str(random.randint(1,9999)),
                   'comment': "%s: %s" % (self.flag_id, flag)}

        r = requests.get("http://%s:%s/cgi-bin/donate.py" % (ip, port), params=payload)
        if r.status_code != requests.codes.ok:
            self.error = 1
            self.error_msg = 'Returned error code %s' % str(r.status_code)
            return
        
        return
    

    def result(self):
        return {'FLAG_ID': self.flag_id, 'TOKEN': self.token, 'ERROR': self.error, 'ERROR_MSG': self.error_msg}


if __name__ == '__main__':
    s = SetFlag()
    s.execute('192.168.56.101', 8112, "FLG1234567890ABC")
    r = s.result()
    print r
 
