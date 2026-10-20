import requests
import sys
#from aifc import data

class GetFlag:
    
    def execute(self, ip, port, flag_id, token):
        self.flag = None
        self.error = 0
        self.error_msg = ''
        
        r = requests.get("http://%s:%s/reports/%s" % (ip, port, token))
        if r.status_code != requests.codes.ok:
            self.error = 1
            self.error_msg = "Cannot retrieve the credit card file %s: %s" % (token, r.status_code)
            return
    
        text = str(r.text)
        #print text
        pos = text.rfind(flag_id)
        if pos < 0:
            self.error = 1
            self.error_msg = "Cannot find the flag_id for token %s: %s" % (token, flag_id)
            return
        
        self.flag = text[pos + len(flag_id) + len(": "):pos + len(flag_id) + len(": ") + 16].strip()

        return
    
    def result(self):
         return{'FLAG':self.flag, 'ERROR': self.error, 'ERROR_MSG': self.error_msg}

