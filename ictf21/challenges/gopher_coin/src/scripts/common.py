import requests 
import json
import struct 
import random
import string

IP = "http://localhost"
PORT = 6666

def flag_id_to_flag(flag_id):
    return f"FLG{str(flag_id).rjust(5, '0')}"

def flag_to_flag_id(flag):
    return int(flag[5:])

def generate_random_flag_id():
    return "F" + "".join([random.choice(string.ascii_uppercase + string.digits) for _ in range(5) ])

def set_connection(ip, port):
    global IP, PORT
    IP = f"http://{ip}"
    PORT = port

#
# Coin Operations
#

def create(abrv, metadata, value, amt):
    req_str = f"{IP}:{PORT}/create?abrv={abrv}&metadata={metadata}&value={value}&amt={amt}" 
    r = requests.get(req_str)
    return r.json()

def update(abrv, metadata, signature):
    req_str = f"{IP}:{PORT}/update?abrv={abrv}&metadata={metadata}&signature={signature}" 
    r = requests.get(req_str)
    return r.json()

def remove(abrv, signature):
    req_str = f"{IP}:{PORT}/remove?abrv={abrv}&signature={signature}" 
    r = requests.get(req_str)
    return r.json()

def list_coins():
    req_str = f"{IP}:{PORT}/list_coins"  
    r = requests.get(req_str)
    return r.json()

def view_coin(abrv, signature):
    req_str = f"{IP}:{PORT}/view_coin?abrv={abrv}&signature={signature}" 
    r = requests.get(req_str)
    return r.json()

#
# User Operations 
#

def register(username, password):
    req_str = f"{IP}:{PORT}/register_user?username={username}&password={password}" 
    r = requests.get(req_str)
    return r.json()

def buy(abrv, amt, username, password):
    req_str = f"{IP}:{PORT}/buy?" \
        f"abrv={abrv}&amt={amt}&" \
        f"username={username}&password={password}" 
    r = requests.get(req_str)
    return r.json()

def sell(abrv, amt, username, password):
    req_str = f"{IP}:{PORT}/sell?" \
        f"abrv={abrv}&amt={amt}&" \
        f"username={username}&password={password}" 
    r = requests.get(req_str)
    return r.json()

def view_wallet(username, password):
    req_str = f"{IP}:{PORT}/view_wallet?username={username}&password={password}"  
    r = requests.get(req_str)
    return r.json()

#
# Utils
#

def generate_broken_signature(timestamp):
    key = b"F"*16
    ts = struct.pack("<Q", timestamp)[:4]
    signature = [0]*8
    for i in range(len(key)):
        signature[i % len(signature)] = key[i] ^ ts[i % len(ts)]

    out = struct.unpack(">Q", bytes(signature))[0]
    
    return hex(out)[2:].rjust(16, "0")
