#!/usr/bin/python
import socket
import sys
import Crypto.Cipher.AES
import base64
import multiprocessing
import datetime
import os
from multiprocessing import Lock, Manager
import logging

class NullDevice():
    def write(self, s):
        pass
    def flush(self):
        pass

sys.stdout = NullDevice()
sys.stderr = NullDevice()


FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(filename="server.log", format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger('server')

logging.disable(logging.CRITICAL)

lock = Lock()

#secret = ks.secret
allowed_commands = set(["ls", "cat secret.txt", "cat server.py"])
#aes_key = ks.aes_key
aes_key = os.urandom(32)
secret = os.urandom(200)
root = "rootadministrator"

manager = Manager()
db = manager.dict()

def safe_string(s):
    return s.isalnum()


def authenticate(s, db, lock):
    

    lock.acquire()
    try:
        fields = s.split("|")
    
        if len(fields) < 2:
            raise Exception("Invalid format")
            return ""

        user = fields[0]
        user = user.strip()
        passwd = fields[1]
        passwd = passwd.strip()
        print user, passwd

        if not (safe_string(user) and safe_string(passwd)):
            raise Exception("Unsafe")
            return ""

        if user == root:
            if passwd == secret:
                print user, "authenticated"
                return user
            else:
                raise Exception("Unauthorized")
                return ""
        else:
            if user in db and db[user] == passwd:
                print user, "authenticated"
                return user
            elif user not in db:
                print user, "authenticated"
                db[user] = passwd
                return user
            else:
                return ""
    except:
        raise
    finally:
        lock.release()
            

def create_token(user):
    try:
        print "creating the token"
        t = datetime.datetime.now()
        plain_token = "%d|%d|%d|%d|%d|%s|CHALLENGE" % (t.year, t.month, t.day, t.hour, t.minute, user)
        l1 = len("%d|%d|%d|%d|%d|" % (t.year, t.month, t.day, t.hour, t.minute))
        padded_plain_token = (" "*(16-(l1%16))) + plain_token
        l = len(padded_plain_token)
        padded_plain_token = padded_plain_token+ (" "*(16-(l%16)))
        aes = Crypto.Cipher.AES.new(aes_key, Crypto.Cipher.AES.MODE_ECB)
        enc_token = aes.encrypt(padded_plain_token)
        b64_token = base64.b64encode(enc_token)
        return b64_token
    except Exception, e:
        logger.error("%s" % str(e))
        raise

def parse_command(msg):
    try:
        fs = msg.split(",")
        b64_c = fs[0]
        command = fs[1]
        command = command.strip()
        print "command=", command
        print "fields=",fs
        c = base64.b64decode(b64_c)
        aes = Crypto.Cipher.AES.new(aes_key, Crypto.Cipher.AES.MODE_ECB)
        m = aes.decrypt(c)
        print "m=", m
        fields = m.split("|")
        year = int(fields[0])
        month = int(fields[1])
        day = int(fields[2])
        hour = int(fields[3])
        minute = int(fields[4])
        user = fields[5]
        user = user.strip()
        print "mfields=", fields
    

        ts = datetime.datetime(year, month, day, hour, minute)
        t = datetime.datetime.now()
        d = t - ts
        if d > datetime.timedelta(seconds=60):
            print "expired"
            raise Exception("Expired")
            return ""

        #authenticated

        if command == "ls":
            print "ls"
            try:
                pipe = os.popen("ls")
                out = pipe.read()
                pipe.close()
            except Exception, e:
                out = ""
            return out
    
        elif command == "cat server.py":
            print "read src"
            try:
                pipe = os.popen("cat server.py")
                out = pipe.read()
                pipe.close()
            except Exception, e:
                out = ""
                raise
            return out

        elif command == "retv secret":
            print "retv"
            if user == root:
                try:
                    pipe = os.popen("cat secret.txt")
                    out = pipe.read()
                    pipe.close()
                
                except Exception, e:
                    out = ""
                    raise
                return out
            else:
                try:
                    try:
                        users_vault = "secret_of_%s.txt" % user
                        pipe = os.popen("cat \"%s\"" % users_vault)
                        out = pipe.read()
                        pipe.close()
                        print "out =", out
                    except Exception, e:
                        out = ""
                        raise
                except:
                    out = ""
                return out
        elif command.startswith("write "):
            print "write"
            to_write = command[len("write "):]
            if user == root:
                try:
                    f = open("secret.txt", "wt")
                    f.write(to_write)
                    f.close()
                except:
                    print "failed"
                    raise

            else:
                try:
                    users_vault = "secret_of_%s.txt" % user
                    f = open(users_vault, "wt")
                    f.write(to_write)
                    f.close()
                except:
                    print "failed"
                    raise


        return ""
        
    except Exception, e:
        print e, "msg=", msg
        raise
        return ""
        
    

def handle(connection, address, db, lock):
    try:
        connection.send("user|pass:")
        data = connection.recv(1024)
        print data, "read"
        user = authenticate(data, db, lock)
        if len(user) == 0:
            raise Exception("Not authenticated")
        print "user %s authenticated" % user
        print "creating token for user", user
        tok = create_token(user)
        print "token=", tok
        connection.send(tok)
        while True:
            connection.send("\ncookie,command:")
            data = ""
            tries = 0
            while len(data) == 0:
                data = connection.recv(1024)
                tries +=1
                if tries > 20:
                    connection.close()
                    return
            print "data=", data
            out = parse_command(data)
            connection.send(out)
    except Exception, e:
        print e
        connection.close()

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', int(sys.argv[1]))
    sock.bind(server_address)
    sock.listen(1)
    processes = []
    lasttime = datetime.datetime.now()
    try:
        while True:
            # Wait for a connection
            now = datetime.datetime.now()
            d = now - lasttime
            if d > datetime.timedelta(seconds=20):
                lasttime = now
                tobe_removed = []
                for i in range(len(processes)):
                    if now - processes[i][1] > datetime.timedelta(seconds=20):
                        try:
                            processes[i][0].terminate()
                        except Exception, e:
                            pass
                        tobe_removed.append(i)
                        #try:
                        #    processes[i][2].close()
                        #except Exception, e:
                        #    pass
                    else:
                        break
                for i in sorted(tobe_removed, reverse=True):
                    del processes[i]
                        
            print >>sys.stderr, 'waiting for a connection'
            connection, client_address = sock.accept()
            process = multiprocessing.Process(target=handle, args=(connection, client_address, db, lock))
            process.daemon = True
            process.start()
            processes.append((process, datetime.datetime.now(), connection))
    except Exception, e:
        print e
        
        
if __name__ == "__main__":
    main()
