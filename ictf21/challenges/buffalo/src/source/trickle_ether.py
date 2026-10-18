import web3
import logging
import os
import sys
import atexit
import json
import time
import glob

PERIOD_SEC = 5 * 60 # every 5 minutes
AMOUNT = 1 # in ether

l = logging.getLogger(__name__)

# configure logging
root_logger = logging.getLogger()
root_logger.handlers = []
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

l.info('Starting up...')

if not os.path.isfile('allkeys.txt'):
    l.error('allkeys.txt must exist')
    exit(1)

if not os.path.isfile('keys/admin.key'):
    l.error('keys/admin.key must exist')
    exit(1)
else:
    with open('keys/admin.key') as fin:
        ADMIN_PRIVKEY = fin.read().strip()
        assert len(ADMIN_PRIVKEY) > 10

if not os.path.isfile('keys/admin.pub'):
    l.error('keys/admin.pub must exist')
    exit(1)
else:
    with open('keys/admin.pub') as fin:
        ADMIN_ADDRESS = fin.read().strip()
        if not ADMIN_ADDRESS.startswith('0x'):
            ADMIN_ADDRESS = '0x' + ADMIN_ADDRESS
        ADMIN_ADDRESS = web3.Web3.toChecksumAddress(ADMIN_ADDRESS)

# create a trickler address (if needed)
if not os.path.isfile('data/trickler_wallet.json'):
    acct = web3.Web3().eth.account.create()
    with open('data/trickler_wallet.json', mode='w') as fout:
        fout.write(json.dumps({'privateKey': acct.privateKey.hex()[2:], 'address': acct.address}))
    l.info('generated account trickler')
with open('data/trickler_wallet.json') as fin:
    trickler_account = json.loads(fin.read())
    trickler_addr = trickler_account['address']
    trickler_key = trickler_account['privateKey']

l.info(f'Sending from address {trickler_account["address"]}')

pubkeys = set()
with open('allkeys.txt') as fin:
    for line in fin:
        if not line.strip() or line.startswith('#'):
            continue
        pubkey = line.split(' ')[2]
        if not pubkey.startswith('0x'):
            pubkey = '0x' + pubkey
        if len(pubkey) != 42:
            l.error(f'Invalid pubkey length: {pubkey}')
            continue
        if not web3.Web3.isAddress(pubkey):
            l.error(f'Not address: {pubkey}')
            continue
        pubkeys.add(pubkey)
l.info(f'Loaded {len(pubkeys)} addresses.')

onetime_payment = set()

if not os.path.isfile('keys/sheep.pub'):
    l.error('keys/sheep.pub must exist')
    exit(1)
else:
    with open('keys/sheep.pub') as fin:
        SHEEP_ADDRESS = fin.read().strip()
        if not SHEEP_ADDRESS.startswith('0x'):
            SHEEP_ADDRESS = '0x' + SHEEP_ADDRESS
        SHEEP_ADDRESS = web3.Web3.toChecksumAddress(SHEEP_ADDRESS)
    onetime_payment.add(SHEEP_ADDRESS)
    l.info('loaded sheep address')


if not os.path.isfile('keys/registry.pub'):
    l.error('keys/registry.pub must exist')
    exit(1)
else:
    with open('keys/registry.pub') as fin:
        REGISTRY_ADDRESS = fin.read().strip()
        if not REGISTRY_ADDRESS.startswith('0x'):
            REGISTRY_ADDRESS = '0x' + REGISTRY_ADDRESS
        REGISTRY_ADDRESS = web3.Web3.toChecksumAddress(REGISTRY_ADDRESS)
    onetime_payment.add(REGISTRY_ADDRESS)
    l.info('loaded registry address')

#
# Load phony addresses
phonies_loaded = 0
for fname in glob.glob('keys/phony/*.pub'):
    with open(fname) as fin:
        key = fin.read().strip()
        if not key.startswith('0x'):
            key = '0x' + key
        key = web3.Web3.toChecksumAddress(key)
        pubkeys.add(key)
        phonies_loaded += 1
l.info(f'Loaded {phonies_loaded} phony addresses')


l.info('Connecting to web3')

w3 = web3.Web3(web3.WebsocketProvider('ws://localhost:8546'))

if not w3.isConnected():
    l.error('w3 connection failed')
    exit(1)

l.info(f'web3 connected to chain_id={w3.eth.chain_id}')

#
# The following would be a great idea if docker gave us enough
# time to do graceful shut-down.
#
# if os.path.isfile('data/trickle.lock'):
#     l.error('lockfile data/trickle.lock exists; quitting')
#     exit(1)
# else:
#     with open('data/trickle.lock', mode='w'):
#         pass

# atexit.register(lambda: os.unlink('data/trickle.lock'))

# ensure that trickler has 10bn ether (idk, seems like a lot)
bal = w3.fromWei(w3.eth.getBalance(trickler_addr), 'ether')
l.info(f'Trickler has balance {bal:,}')
diff = 10_000_000_000 - bal
if diff > 0:
    l.info(f'Sending {diff} ETH to trickler')
    txn_ct = w3.eth.get_transaction_count(ADMIN_ADDRESS)
    tx = {
        'nonce': txn_ct,
        'to': trickler_addr,
        'value': w3.toWei(diff, 'ether'),
        'gas': 2000000,
        'chainId': w3.eth.chain_id,
        'gasPrice': w3.eth.gas_price * 2, # we get it for free?
    }
    signed_tx = w3.eth.account.sign_transaction(tx, ADMIN_PRIVKEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    l.info(f'sent txn {tx_hash}')
    while True:
        l.info(f'watching for completion of {tx_hash}')
        time.sleep(1)
        new_txn = w3.eth.get_transaction(tx_hash)
        if new_txn['blockNumber'] is not None:
            break
    l.info('sent')



while True:
    txn_ct = w3.eth.get_transaction_count(trickler_addr)
    next_nonce = txn_ct
    gas_price = w3.eth.gas_price
    l.info(f'trickler transaction_count={txn_ct}')
    
    #
    # generate transactions to send out
    
    # mapping from hash to transaction
    txns_tosend = {}
    for dest in pubkeys.union(onetime_payment):
        assert dest is not None
        assert dest != '0x' and dest != ''

        while True:
            tx = {
                'nonce': next_nonce,
                'to': dest,
                'value': w3.toWei(AMOUNT, 'ether'),
                'gas': 2000000,
                'chainId': w3.eth.chain_id,
                'gasPrice': gas_price * 2, # we get it for free?
            }
            next_nonce += 1
            signed_tx = w3.eth.account.sign_transaction(tx, trickler_key)
            try:
                tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                txns_tosend[tx_hash] = {'raw_tx': tx}
                break
            except ValueError as e:
                if '-32000' in str(e):
                    l.warning('nonce conflict, trying again')
                else:
                    raise e

    # watch for this to finish
    completed_txns = set()
    error_txns = set()
    while len(completed_txns.union(error_txns)) != len(txns_tosend):
        time.sleep(2.5) # quarter block time
        # if the nonce hasn't increased, keep polling
        if txn_ct == w3.eth.get_transaction_count(trickler_addr):
            continue
        for h in set(txns_tosend.keys()).difference(completed_txns).difference(error_txns):
            new_txn = w3.eth.get_transaction(h)
            if new_txn is None:
                l.error(f'Could not re-find transaction {h}')
                error_txns.add(h)
            if new_txn['blockNumber'] is not None:
                completed_txns.add(h)

    l.info('Distributed money.')
    with open('data/.initial_distribution', mode='w'):
        pass
    onetime_payment = set()

    l.info(f'Sleeping for {PERIOD_SEC} seconds')
    time.sleep(PERIOD_SEC)
