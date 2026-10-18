import json
import hashlib
import random
import secrets
import ssl
import time

from urllib import request

HASHES = {
    '':              '5f20c391f28adf0bf85617bcf2fda048',
    'get.html':      '21d91913fc4def5e6bf46f0e4d4da285',
    'index.html':    '5f20c391f28adf0bf85617bcf2fda048',
    'new.html':      'ea446be1bb09d0c592a679079498d096',
    'set.html':      '17a623de143929449d9738c4089c94e7',
    'web/logo.png':  '42b42b170e6bdd02b138333e2766ca8a',
    'web/logo.svg':  '950008fa1682c03a6b142ee4e6a31443',
    'web/script.js': '13740df267e2e34810a4c515b840d104',
    'web/style.css': '8ab757656c1fe4459a839a221887f516',
}

def create_pass():
    return secrets.token_urlsafe(24)

def create_flag():
    return 'FLG' + secrets.token_hex(24)


def trim(string, length=32):
    if len(string) > length:
        return string[:length-3] + '...'
    return string

def req(url, data=None):
    if data is not None:
        data = json.dumps(data).encode('utf-8')
        # print(data)

    # print(url)
    with request.urlopen(url, data=data, timeout=5, context=ssl.SSLContext()) as response:
        if response.getcode() != 200:
            raise Exception('Request failed (%d): %s' % (
                response.getcode(),
                trim(response.read())
            ))
        return response.read()

def get(host, port, path):
    return req('https://%s:%d/%s' % (host, port, path))

def get_checked(host, port, path):
    if hashlib.md5(get(host, port, path)).hexdigest() != HASHES[path]:
        raise Exception('Incorrect file returned: ' + path)

def post(url, data):
    text = req(url, data)
    # print(text)
    data = json.loads(text)
    # print(data)
    return data

def create_account(host, port, password, comment):
    get_checked(host, port, 'new.html')
    return post('https://%s:%d/new' % (host, port), {
        'password': password,
        'comment':  comment
    })

def update_account(host, port, address, password, comment):
    get_checked(host, port, 'set.html')
    return post('https://%s:%d/set' % (host, port), {
        'address':  address,
        'password': password,
        'comment':  comment
    })

def retrieve_account(host, port, address, password, version=None):
    get_checked(host, port, 'get.html')
    return post('https://%s:%d/get' % (host, port), {
        'address':  address,
        'password': password,
        'version':  version
    })


def check_random(host, port, n, sleep=True):
    for path in random.sample(HASHES.keys(), n):
        get_checked(host, port, path)
        if sleep:
            time.sleep(random.randrange(5))

def check_series(host, port, n, m, password=None, flag=None, sleep=True):
    if n == 0:
        return

    if password is None:
        password = create_pass()
    comments = [create_flag() for _ in range(n)]
    address  = None
    flag_id  = None

    if flag is not None:
        flag_id = random.randrange(n)
        comments[flag_id] = flag

    # Store a bunch of flags:
    collected = []
    for i, c in enumerate(comments):
        if address is None:
            data = create_account(host, port, password, c)
            address = data['address']
        else:
            data = update_account(host, port, address, password, c)
        if data['version'] != i + 1:
            raise Exception('Incorrect version returned.')
        if sleep:
            time.sleep(random.randrange(5))
        collected.append(data)

    # Make sure that we can get a random flag:
    i = random.randrange(n)
    version = collected[i]['version']
    data = retrieve_account(host, port, address, password, version)
    if data['address'] != collected[i]['address']:
        raise Exception('Incorrect address retrieved.')
    if data['comment'] != comments[i]:
        raise Exception('Incorrect comment retrieved.')
    if data['version'] != version:
        raise Exception('Incorrect version retrieved.')
    # if data['public-key'] != address:
    #     raise Exception('Incorrect public key format.')
    # if data['secret-key'] != address:
    #     raise Exception('Incorrect secret key format.')

    if flag is not None:
        # print('COLLECTED', collected[flag_id], flush=True)
        return "{address:s}v{version:d}".format(**collected[flag_id])
