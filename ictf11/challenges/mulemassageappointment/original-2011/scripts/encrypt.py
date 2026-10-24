import rsa
import sys
import urllib

if len(sys.argv) != 2:
    print 'Please provide a flag to encrypt'
    sys.exit(1)
pubkey=rsa.PublicKey.load_pkcs1(open("pub.key").read())
print urllib.quote(rsa.encrypt(sys.argv[1], pubkey))
