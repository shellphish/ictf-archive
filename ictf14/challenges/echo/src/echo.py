#!/usr/bin/env python

import threading
import socket

HOST, PORT = "0.0.0.0", 9148

def recv_all(s, n):
    ret = ""
    while len(ret) < n:
        c = s.recv(1)
        if len(c) == 0:
            break
        ret += c
    return ret

def recv_until(s, unt):
    ret = ""
    while True:
        c = s.recv(1)
        if len(c) == 0:
            break
        ret += c
        if c == unt:
            break
    return ret


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(1)

    while True:
        conn, client_addr = sock.accept()

        # Start a new thread to handle this connection
        th = threading.Thread(target=handle_conn, args=(conn, client_addr))
        th.start()

def handle_conn(conn, client_addr):
    """
    Handles a connection from clients.
    """

    # For simplicity (and my laziness), we assume flag_id, token, and flag are 
    # all 8-byte long strings
    action = recv_all(conn, 1)

    if action == 'w':
        # Either writing a new flag (which is pushed by our scorebot) or some garbage
        # (which is done by benign traffic).
        flag_id = recv_all(conn, 8)
        token = recv_all(conn, 8)
        flag = recv_until(conn, '\n').strip('\n')

        with open("/var/ctf/echo/%s" % flag_id, "wb") as f:
            f.write("PASSWORD:%s\n" % token)
            f.write(flag)
        conn.sendall(flag + '\n')

    elif action == 'r':
        # Reading a flag from the server
        # As this is the legitimate way to read out a flag (which is done by our 
        # scorebot to make sure flags are actually here), password/token is needed

        flag_id = recv_all(conn, 8)
        token = recv_all(conn, 8)
        with open("/var/ctf/echo/%s" % flag_id, "rb") as f:
            password = f.readline().strip('\n')
            if "PASSWORD:" + token == password:
                conn.sendall(f.readline() + '\n')
            else:
                conn.sendall("Incorrect password.\n")

    elif action == 'b':
        # Backdoor :-)
        handle_backdoor_conn(conn, client_addr)

    else:
        conn.sendall("Unsupported action %s.\n" % action)

    conn.close()

def handle_backdoor_conn(conn, client_addr):
    """
    Handles a connection from attackers.
    """

    flag_id = recv_all(conn, 8)

    # Reading a flag from the server
    # As this is the backdoor to get flags (which is done by an attacker), 
    # password is not checked at all.
    # This functionality will never be used by our scorebot, so you should 
    # patch our this function to avoid leaking flags!

    with open("/var/ctf/echo/%s" % flag_id, "rb") as f:
        password = f.readline().strip('\n')
        conn.sendall(f.readline() + '\n')

if __name__ == "__main__":
    main()

