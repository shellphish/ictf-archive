import random,string,time,struct,socket
from subprocess import Popen, PIPE
class Benign():
  def execute(self,ip,port,flag_id,token):
    flag=''.join(random.choice(string.ascii_letters) for i in xrange(16))
    cookie = random.choice(string.ascii_lowercase) + ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(5))
    carriers = ("T-Mobile", "Verizon", "AT&T", "Sprint") # Pick random among these
    msgtime = time.strftime("%Y-%m-%d %H:%M:%S")
    sender = cookie
    subject = flag
    p = Popen(["/usr/games/fortune", "-s"], stdout=PIPE, stderr=PIPE)
    msgbody = p.communicate()[0]

    phone_numbers = list()
    for i in range(random.choice(range(1, 21))):
        phone_numbers.append("%s:%s" % (random.choice(carriers), "+1 (%s) %s-%s" %(random.randrange(100,999), random.randrange(100,999), random.randrange(1000,9999))))

    num_devices = len(phone_numbers)
    aggregator_msg = struct.pack("!I", len(msgtime)) + struct.pack("%ds" % len(msgtime), str(msgtime))
    aggregator_msg = aggregator_msg + struct.pack("!I", len(sender)) + struct.pack("%ds" % len(sender), str(sender))
    aggregator_msg = aggregator_msg + struct.pack("!I", len(subject)) + struct.pack("%ds" % len(subject), str(subject))
    aggregator_msg = aggregator_msg + struct.pack("!I", len(msgbody)) + struct.pack("%ds" % len(msgbody), str(msgbody))
    aggregator_msg = aggregator_msg + struct.pack("!I", num_devices)
    offset = 0
    i = 0
    phonelist = ""
    for device_descriptor in phone_numbers:
        aggregator_msg = aggregator_msg + struct.pack("!I", offset)
        phonelist = phonelist + struct.pack("!I", 0) + struct.pack("!I", len(device_descriptor)) + struct.pack("%ds" % len(device_descriptor), str(device_descriptor))
        offset = offset + 4 + 4 + len(device_descriptor)
        i = i + 1
    aggregator_msg = aggregator_msg + phonelist
    total_len = len(aggregator_msg)
    msg = struct.pack("!I", total_len) + aggregator_msg
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    smsfd = s.makefile()
    s.send(msg)
    flag = ""
    while True:
        response = smsfd.readline().strip()
        if response == "":
            break;
        actual_response = response.split(":")[-1]
        if len(actual_response) > 0:
            flag = actual_response
    s.close()

    self.error=0;self.error_msg=""
  def result(self):
    return {'ERROR':self.error,'ERROR_MSG':self.error_msg}
