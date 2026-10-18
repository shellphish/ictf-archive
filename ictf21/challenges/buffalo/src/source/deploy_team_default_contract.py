"""
deploy_team_default_contract.py

Deploys the default contract for each team.
If the contract is already deployed, then this is a no-op.
"""
import time
from web3.middleware import geth_poa_middleware
import web3
import os
import logging
import sys
import json
import rlp

l = logging.getLogger(__name__)

# configure logging
root_logger = logging.getLogger()
root_logger.handlers = []
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

l.info('Starting default contract deployer')

# Find contract artifact location: may be in one of two places
if os.path.isfile('PhishToken.json'):
    CONTRACT_PATH = 'PhishToken.json'
elif os.path.isfile('artifacts/contracts/nft.sol/PhishToken.json'):
    CONTRACT_PATH = 'artifacts/contracts/nft.sol/PhishToken.json'
else:
    l.error('Could not find contract json')
    exit(1)

l.info(f'Using contract at {CONTRACT_PATH}')

with open(CONTRACT_PATH) as fin:
    CONTRACT_ARTIFACT = json.loads(fin.read())

if not 'bytecode' in CONTRACT_ARTIFACT:
    l.error('Could not find contract bytecode')

# Find registry artifact location: may be in one of two places
if os.path.isfile('Registry.json'):
    REGISTRY_CONTRACT_PATH = 'Registry.json'
elif os.path.isfile('artifacts/contracts/registry.sol/Registry.json'):
    REGISTRY_CONTRACT_PATH = 'artifacts/contracts/registry.sol/Registry.json'
else:
    l.error('Could not find registry contract json')
    exit(1)

l.info(f'Using registry contract at {REGISTRY_CONTRACT_PATH}')

with open(REGISTRY_CONTRACT_PATH) as fin:
    REGISTRY_CONTRACT_ARTIFACT = json.loads(fin.read())

if not 'bytecode' in REGISTRY_CONTRACT_ARTIFACT:
    l.error('Could not find registry contract bytecode')


# Get all team keypairs
TEAM_KEYPAIRS = []
if not os.path.isfile('allkeys.txt'):
    l.error('Could not find allkeys.txt')
    exit(1)
with open('allkeys.txt') as fin:
    loaded_addrs = set()
    for line in fin:
        if not line.strip() or line.startswith('#'):
            continue
        _, _, addr, key = line.strip().split(' ')
        if not web3.Web3.isAddress(addr):
            l.error(f'Not address: {addr}')
            exit(1)
        if addr in loaded_addrs:
            l.error(f'Duplicate key: {addr}')
            exit(1)
        loaded_addrs.add(addr)
        TEAM_KEYPAIRS.append((addr, key))

l.info(f'Loaded {len(TEAM_KEYPAIRS)} team keypairs')

# Get admin keypair
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


# Get sheep keypair
if not os.path.isfile('keys/sheep.key'):
    l.error('keys/sheep.key must exist')
    exit(1)
else:
    with open('keys/sheep.key') as fin:
        SHEEP_PRIVKEY = fin.read().strip()

if not os.path.isfile('keys/sheep.pub'):
    l.error('keys/sheep.pub must exist')
    exit(1)
else:
    with open('keys/sheep.pub') as fin:
        SHEEP_ADDRESS = fin.read().strip()
        if not SHEEP_ADDRESS.startswith('0x'):
            SHEEP_ADDRESS = '0x' + SHEEP_ADDRESS
        SHEEP_ADDRESS = web3.Web3.toChecksumAddress(SHEEP_ADDRESS)
TEAM_KEYPAIRS.append((SHEEP_ADDRESS, SHEEP_PRIVKEY))


# Get registry keypair
if not os.path.isfile('keys/registry.key'):
    l.error('keys/registry.key must exist')
    exit(1)
else:
    with open('keys/registry.key') as fin:
        REGISTRY_PRIVKEY = fin.read().strip()

if not os.path.isfile('keys/registry.pub'):
    l.error('keys/registry.pub must exist')
    exit(1)
else:
    with open('keys/registry.pub') as fin:
        REGISTRY_ADDRESS = fin.read().strip()
        if not REGISTRY_ADDRESS.startswith('0x'):
            REGISTRY_ADDRESS = '0x' + REGISTRY_ADDRESS
        REGISTRY_ADDRESS = web3.Web3.toChecksumAddress(REGISTRY_ADDRESS)


l.info('Connecting to web3')
w3 = web3.Web3(web3.WebsocketProvider('ws://localhost:8546'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

if not w3.isConnected():
    l.error('w3 connection failed')
    exit(1)

l.info(f'web3 connected to chain_id={w3.eth.chain_id}')

# figure out how much deployment will take
contract = w3.eth.contract(bytecode=CONTRACT_ARTIFACT['bytecode'], abi=CONTRACT_ARTIFACT['abi'])
txn = contract.constructor('PhishToken', 'PTK', 'ptk://').buildTransaction({'from': ADMIN_ADDRESS})
gas = w3.eth.estimate_gas(txn)
l.info(f'Estimate gas usage for deploying contract: {gas}')

gasprice = w3.eth.gas_price
l.info(f'Estimate gas_price={gasprice}')

txn_cost_wei = gas * gasprice
txn_cost_ether = w3.fromWei(gas * gasprice, 'ether')
l.info(f'Transaction cost to create contract: {txn_cost_ether} ETH')

while not os.path.isfile('data/.initial_distribution'):
    l.info(f'Waiting for initial distribution of funds to complete...')
    time.sleep(2.5)

# start deploying the contracts
create_txns = {}
for addr, key in TEAM_KEYPAIRS:
    if w3.eth.get_transaction_count(addr) != 0:
        #
        # The contract should have already been deployed
        baddr = bytes.fromhex(addr[2:])
        expected = w3.toChecksumAddress(w3.keccak(rlp.encode([baddr, 0]))[12:].hex())
        got_code = w3.eth.get_code(expected)
        if not got_code:
            l.error(f'Could not find first contract for {addr}; expected {expected}')
            exit(1)
        if not got_code.hex() == CONTRACT_ARTIFACT['deployedBytecode']:
            print(got_code.hex())
            l.error('unexpected code difference')
            exit(1)
    else:
        # ensure we have enough ETH for this
        for _ in range(4):
            bal = w3.eth.get_balance(addr)
            if bal > txn_cost_ether:
                break
            time.sleep(5)
        else:
            l.error(f'Account {addr} did not have enough balance')
            exit(1)


        txn = contract.constructor('PhishToken', 'PTK', 'ptk://').buildTransaction({'from': addr})
        txn['nonce'] = 0
        txn['chainId'] = w3.eth.chain_id
        txn['gasPrice'] = gasprice
        signed = w3.eth.account.sign_transaction(txn, key)
        txn_hash = w3.eth.send_raw_transaction(signed.rawTransaction).hex()
        l.info(f'Sent create transaction {txn_hash}')
        create_txns[txn_hash] = addr

# If the registry is not deployed, do that
registry_contract = w3.eth.contract(bytecode=REGISTRY_CONTRACT_ARTIFACT['bytecode'], abi=REGISTRY_CONTRACT_ARTIFACT['abi'])
if w3.eth.get_transaction_count(REGISTRY_ADDRESS) == 0:
    l.info('Deploying the registry.')
    txn = registry_contract.constructor().buildTransaction({'from': REGISTRY_ADDRESS})
    txn['nonce'] = 0
    txn['chainId'] = w3.eth.chain_id
    txn['gasPrice'] = gasprice
    signed = w3.eth.account.sign_transaction(txn, REGISTRY_PRIVKEY)
    txn_hash = w3.eth.send_raw_transaction(signed.rawTransaction).hex()
    create_txns[txn_hash] = REGISTRY_ADDRESS
    l.info(f'Sent create registry transaction {txn_hash}')

l.info('Watching to ensure completion')

#
# wait for contracts + registry to deploy

completed = set()
addr_to_contract = {}
while len(set(create_txns.keys()).difference(completed)) > 0:
    l.info('sleeping for a bit, then checking for completion...')
    time.sleep(2.5)
    for txn in set(create_txns.keys()).difference(completed):
        got_txn = w3.eth.get_transaction(txn)
        if got_txn is None:
            l.error(f'Could not re-find transaction {txn}')
            exit(1)
        if got_txn['blockNumber'] is not None:
            completed.add(txn)
            receipt = w3.eth.get_transaction_receipt(txn)
            contract_addr = w3.toChecksumAddress(
                receipt['contractAddress']
            )
            from_ = w3.toChecksumAddress(receipt['from'])
            addr_to_contract[from_] = contract_addr
            l.info(f'address {from_} created contract {contract_addr}')

#
# setup the registry

bregaddr_sender = bytes.fromhex(REGISTRY_ADDRESS[2:])
reg_contract_addr = w3.toChecksumAddress(w3.keccak(rlp.encode([bregaddr_sender, 0]))[12:].hex())
with open('data/registry_addr.txt', mode='w') as fin:
    fin.write(f'{reg_contract_addr}\n')
l.info(f'Using registry at {reg_contract_addr}')
registry_contract = w3.eth.contract(address=reg_contract_addr, abi=REGISTRY_CONTRACT_ARTIFACT['abi'])

# Ensure all teams have (at least) their default contract registered
register_txns = set()
for addr, key in TEAM_KEYPAIRS:
    c = registry_contract.functions.getContract(addr).call()
    if c == '0x0000000000000000000000000000000000000000':
        # need to register
        l.info(f'Registering default contract for team address {addr}')
        contract_addr = addr_to_contract[addr]
        txn = registry_contract.functions.register(contract_addr).buildTransaction({'from': addr})
        txn['nonce'] = w3.eth.get_transaction_count(addr)
        txn['chainId'] = w3.eth.chain_id
        txn['gasPrice'] = gasprice
        signed_txn = w3.eth.account.sign_transaction(txn, key)
        txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        register_txns.add(txn_hash)
    else:
        l.info(f'Addr {addr} already registered at {c}')

# await all contracts' completion
completed = set()
while len(register_txns.difference(completed)) > 0:
    l.info('sleeping for a bit, then checking for completion...')
    time.sleep(2.5)
    for txn in register_txns.difference(completed):
        got_txn = w3.eth.get_transaction(txn)
        if got_txn is None:
            l.error(f'Could not re-find transaction {txn}')
            exit(1)
        if got_txn['blockNumber'] is not None:
            completed.add(txn)


l.info('Done.')

