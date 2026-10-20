import re


def recv_until(s, endmsg):
    msg = ''
    while True:
        part = s.recv(2048);
        msg += part
        if msg.find(endmsg) >= 0:
            break
    return msg


def get_id_from_plant_name(s, plant_name):
    s.send('2\n')

    msg = recv_until(s, 'Your choice: ')
    print msg
    m = re.search('Plant \(#([0-9]+)\): %s' % plant_name, msg)
    plant_id = -1
    if m:
        print 'FOUND: %s' % m.group(1)
        plant_id = int(m.group(1))
    else:
        raise Exception('flag_id not found')

    return plant_id
