import time
import requests

class GetFlag(object):
    def __init__(self):
        self.flag = ""
        self.error = 1
        self.error_msg = "execute() is not called."

    def execute(self, ip, port, flag_id, token):
        url_base = "http://%s:%d/cgi-bin/diebald.cgi" % (ip, port)
        r = requests.get(url_base, params={
                                            'op': 'gettask',
                                            'username': flag_id,
                                            'password': token
                                            }
        )

        if "Task to be done by" not in r.text or \
                "<pre>" not in r.text or \
                "</pre>" not in r.text:
            self.error = 2
            self.error_msg = "Incorrect page content."

        self.flag = r.text[r.text.find("<pre>") + 5 : r.text.find("</pre>")].strip('\n')
        self.error = 0
        self.error_msg = ""

    def result(self):
        return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}

if __name__ == "__main__":
    import sys
    gf = GetFlag()
    gf.execute(sys.argv[1], 8012, sys.argv[2], sys.argv[3])
    print gf.result()

