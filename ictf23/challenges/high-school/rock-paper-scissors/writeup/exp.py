from pwn import *

conn = process('./rps.py')

recv_mark = 'Your throw:'.encode('ascii')
recv_bot = lambda x: conn.recvuntil(x).decode()
throw = lambda x: conn.send(f'{x}\n'.encode('ascii'))

conn.recvuntil('Remember across games? (y/n):'.encode('ascii'))
conn.send('n\n'.encode('ascii'))

# phase 1
while True:
    if 'smart' in recv_bot(recv_mark): break
    throw('r')

# phase 2
throw('p')
recv_bot(recv_mark)
throw('s')
recv_bot(recv_mark)
throw('r')
recv_bot(recv_mark)
throw('p')
recv_bot(recv_mark)

# phase 3
nexts = ['p', 'r', 'r', 's', 's', 'p', 's', 'r', 'p']*100
msg = ''
for next in nexts:
    if 'Rounds to win: 1 ' in msg:
        throw(next)
        for i in range(12): conn.recvline()
        print(conn.recvline().decode())
        break

    throw(next)
    msg = recv_bot(recv_mark)
