from pwn import *
import re
import random
from tqdm import tqdm

p = remote("localhost", 28443)

seen_hashes = {}
target_classroom_amount = 10000

p.recvuntil(b"Enter your name: ")
p.sendline(b'a')
p.recvuntil(b"Enter your grade: ")
p.sendline(b'a')
p.recvuntil(b"Enter your date of birth: ")
p.sendline(b'a')
p.recvuntil(b"Your ID: ")
new_id = p.recvline().decode().strip()
p.recvuntil(b"Choose your next action:")

for i in tqdm(range(1, target_classroom_amount + 1)):
    p.sendline(b"1")
    p.recvuntil(b"Check a classroom: ")
    p.sendline(str(i).encode())

    classroom_output = p.recvuntil(b"Choose your next action:")
    student_ids = re.findall(rb"Student \d+'s ID: (\S+)", classroom_output)

    for stu in student_ids:
        seen_hashes[stu.decode()] = i

uniq_ids = len(seen_hashes.keys())
print("Unique student IDs: ", uniq_ids)
print("Estimated tries: ", 1 / (uniq_ids / (2**28)))
p.sendline(b"1")
p.recvuntil(b"Check a classroom: ")
p.sendline(b"0")

pbar = tqdm()
while True:
    p.recvuntil(b"Enter your name: ")
    p.sendline(b'a')
    p.recvuntil(b"Enter your grade: ")
    p.sendline(b'a')
    p.recvuntil(b"Enter your date of birth: ")
    p.sendline(str(random.randint(0, 2**32)).encode())
    p.recvuntil(b"Your ID: ")
    new_id = p.recvline().decode().strip()

    p.recvuntil(b"Choose your next action:")
    p.sendline(b"1")
    p.recvuntil(b"Check a classroom: ")

    if new_id in seen_hashes:
        class_num = seen_hashes[new_id]
        p.sendline(str(class_num).encode())
        p.recvuntil(b"Is your name really")
        print(p.recvuntil(b"}").decode().strip())
        exit()
    p.sendline(b"0")

    pbar.update(1)
