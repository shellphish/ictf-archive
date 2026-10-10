import socket, time, sys, getopt

timeout=30

def usage(fname):
    print "%s [-i <mothership_ip>] [-p <mothership_port>]" % fname


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    if argv is None:
        argv = sys.argv
    mother_ip = "10.14.0.100"
    mother_port = 8080
    try:
        opts, args = getopt.getopt(argv[1:], "i:p:")
    except getopt.error, msg:
        raise Usage(msg)
    for o, a in opts:
        if o == "-i":
            mother_ip = a
        if o == "-p":
            mother_port = int(a)
    while True:
        try:
            mother = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mother.connect((mother_ip, mother_port))
            while True:
                mother.send("aGVhcnRiZWF0Cg==\n")
                time.sleep(timeout)
        except Exception, err:
            print "exception", str(err)
            mother.close()
            time.sleep(timeout)
        except (KeyboardInterrupt, SystemExit):
            mother.close()
            return

if __name__ == '__main__':
    sys.exit(main())

