#!/usr/bin/enb python3
import glob
import random
import time
import json
import os
import rlp
import sys
import asyncio
import logging
import web3
import web3.contract
import sqlite3
import hashlib
import atexit

l = logging.getLogger(__name__)

#
# configure logging
#
root_logger = logging.getLogger()
root_logger.handlers = []
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

l.info('Starting up...')

l.info('loading ip to team key mapping')
ip_to_team_addr = {}
team_addr_to_sha1_token = {}
with open('allkeys.txt') as fin:
    for line in fin:
        if line.startswith('#'):
            continue
        ip, access_token, addr, _ = line.strip().split(' ')
        assert web3.Web3.isChecksumAddress(addr)
        ip_to_team_addr[ip] = addr

        h = hashlib.sha1()
        h.update(access_token.encode('ascii'))
        team_addr_to_sha1_token[addr] = h.digest()
l.info(f'loaded {len(ip_to_team_addr)} known team ips')

with open('keys/registry.pub') as fin:
    registry_addr = fin.read().strip()
    if not registry_addr.startswith('0x'):
        registry_addr = '0x' + registry_addr
    registry_addr = web3.Web3.toChecksumAddress(registry_addr)
    assert len(registry_addr) == 42
bregaddr_sender = bytes.fromhex(registry_addr[2:])
reg_contract_addr = web3.Web3.toChecksumAddress(web3.Web3.keccak(rlp.encode([bregaddr_sender, 0]))[12:].hex())

l.info(f'registry addr = {reg_contract_addr}')

with open('keys/admin.pub') as fin:
    admin_addr = fin.read().strip()
    if not admin_addr.startswith('0x'):
        admin_addr = '0x' + admin_addr
    admin_addr = web3.Web3.toChecksumAddress(admin_addr)
    assert len(admin_addr) == 42

l.info(f'admin addr = {admin_addr}')

with open('keys/admin.key') as fin:
    admin_key = fin.read().strip()

l.info('loaded admin key')

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

# get the registry abi
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

global_lock = asyncio.Lock()
db = sqlite3.connect('data/flagstate.db')
atexit.register(lambda: db.close())
curr = db.cursor()

curr.execute("CREATE TABLE IF NOT EXISTS flags (contract_addr TEXT, root TEXT, flag TEXT, created_at FLOAT)")
curr.execute("CREATE INDEX IF NOT EXISTS flags_contract ON flags (contract_addr)")
curr.execute("CREATE INDEX IF NOT EXISTS flags_stub ON flags (root)")

while not os.path.isfile('data/.initial_distribution'):
    l.info('waiting for initial distribution to complete')
    time.sleep(2.5)

# we should have exclusive access to admin nonce now, we'll protect it by the global lock
w3 = web3.Web3(web3.WebsocketProvider('ws://127.0.0.1:8546'))
admin_nonce = w3.eth.get_transaction_count(admin_addr)
l.info(f'admin nonce = {admin_nonce}')
del w3
used_admin_nonces = set()


async def setflag(reader, writer, w3):
    # next line will be <ip> <flag>
    line = await reader.readline()
    ip, flag = line.decode('ascii').strip().split(' ')
    if ip not in ip_to_team_addr:
        l.error(f'bad ip supplied, unknown: {ip}')
        return
    team_addr = ip_to_team_addr[ip]

    registry_contract = w3.eth.contract(address=reg_contract_addr, abi=REGISTRY_CONTRACT_ARTIFACT['abi'])
    c = registry_contract.functions.getContract(team_addr).call()

    team_contract = w3.eth.contract(address=c, abi=CONTRACT_ARTIFACT['abi'])

    h = hashlib.md5()
    h.update(flag.encode('ascii'))
    h.update(b'My super secret hash salt that nobody could ever guess because it is entirely too long.\n')
    d = h.digest()[:16]
    root = w3.toInt(d)
    l.info(f'setflag for ip={ip}, team_addr={team_addr}, contract={c}, root={root}')

    async with global_lock:
        if len(used_admin_nonces) > 0:
            trying_nonce = max(w3.eth.get_transaction_count(admin_addr), max(used_admin_nonces) + 1)
        else:
            trying_nonce = w3.eth.get_transaction_count(admin_addr)
        for i in range(500):
            l.info(f'On attempt number {i+1} for nonce')
            my_nonce = trying_nonce + i
            if my_nonce in used_admin_nonces:
                continue
            txn = team_contract.functions.registerRoot(root).buildTransaction({'from': admin_addr})
            txn['nonce'] = my_nonce
            txn['chainId'] = w3.eth.chain_id
            txn['gasPrice'] = w3.eth.gas_price
            signed = w3.eth.account.sign_transaction(txn, admin_key)
            try:
                txn_hash = w3.eth.send_raw_transaction(signed.rawTransaction).hex()
                used_admin_nonces.add(my_nonce)
                break
            except Exception as e:
                if 'replacement transaction underpriced' in str(e):
                    l.info('nonce failed, retrying')
                    used_admin_nonces.add(my_nonce)
                    continue
                writer.write(b'FAILED\n')
                await writer.drain()
                raise e
        else:
            writer.write(b'FAILED\n')
            await writer.drain()
            raise Exception('nonce failed too many times')
    l.info(f'Transmitted transaction hash {txn_hash}')

    start = time.time()
    while time.time() - start < 60: # 60s timeout, idk
        l.info(f'Watching to ensure completion of {txn_hash}')
        new_txn = w3.eth.get_transaction(txn_hash)
        if new_txn['blockNumber'] is not None:
            break
        await asyncio.sleep(1)
    else:
        l.error(f'TIMEOUT on transaction {txn_hash}')

    async with global_lock:
        curr.execute(
            "INSERT INTO flags (contract_addr, root, flag, created_at) VALUES (?, ?, ?, ?)",
            (c, str(root), flag, time.time())
        )
        db.commit()
    flagid = f"CONTRACT:{c};ROOT:{root}"
    l.info(f'new flag id: {flagid}')
    writer.write(f'SUCCESS {flagid}\n'.encode('ascii'))
    await writer.drain()
    l.info(f'Transaction completed: {txn_hash}')


async def getflag(reader, writer, w3: web3.Web3):
    # next line will be <ip> <flag_id>
    ip, flag_id = (await reader.readline()).decode('ascii').strip().split(' ')
    if ip not in ip_to_team_addr:
        l.error(f'bad ip supplied, unknown: {ip}')
        return

    splat = flag_id.split(';')
    c = splat[0].split(':')[1]
    root = splat[1].split(':')[1]

    team_contract = w3.eth.contract(address=c, abi=CONTRACT_ARTIFACT['abi'])

    l.info(f'getflag; contract={c}, root={root}')

    l.info(f'pulling a token through {c}')
    async with global_lock:
        if len(used_admin_nonces) > 0:
            trying_nonce = max(w3.eth.get_transaction_count(admin_addr), max(used_admin_nonces) + 1)
        else:
            trying_nonce = w3.eth.get_transaction_count(admin_addr)
        for i in range(100):
            l.info(f'On attempt number {i+1} for nonce')
            my_nonce = trying_nonce + i
            if my_nonce in used_admin_nonces:
                continue
            txn = team_contract.functions.requestToken(int(root), admin_addr).buildTransaction({'from': admin_addr})
            txn['nonce'] = my_nonce
            txn['chainId'] = w3.eth.chain_id
            txn['gasPrice'] = w3.eth.gas_price
            signed = w3.eth.account.sign_transaction(txn, admin_key)
            try:
                txn_hash = w3.eth.send_raw_transaction(signed.rawTransaction).hex()
                used_admin_nonces.add(my_nonce)
                break
            except Exception as e:
                if 'replacement transaction underpriced' in str(e):
                    l.info('nonce failed, retrying')
                    used_admin_nonces.add(my_nonce)
                    continue
                writer.write(b'FAILED\n')
                await writer.drain()
                raise e
        else:
            writer.write(b'FAILED\n')
            await writer.drain()
            raise Exception('nonce failed too many times')
    l.info(f'Transmitted transaction hash {txn_hash}')

    # see if it completes
    start = time.time()
    while time.time() - start < 60: # 60s timeout, idk
        l.info(f'Watching to ensure completion of {txn_hash}')
        new_txn = w3.eth.get_transaction(txn_hash)
        if new_txn['blockNumber'] is not None:
            #
            # TODO ensure that the receipt parses with a transaction event
            break
        await asyncio.sleep(1)
    else:
        l.error(f'TIMEOUT on transaction {txn_hash}')
        writer.write(b'TIMEOUT-FAILED\n')
        await writer.drain()
        return

    receipt = w3.eth.get_transaction_receipt(txn_hash)
    logs = team_contract.events.Transfer().processReceipt(receipt, errors=web3.logs.DISCARD)
    if len(logs) != 1:
        l.info(f'Expected exactly 1 relevant log in transaction, but got {len(logs)}')
        writer.write(b'ERROR-NO-LOGS-FAILED\n')
        await writer.drain()
        return

    log = logs[0]
    token_id = log['args']['tokenId']
    found_tag = token_id >> 128
    if str(found_tag) != root:
        l.info(f'Contract {c} supplied wrong tag!')
        writer.write(b'ERROR-WRONG-TAG\n')
        await writer.drain()
        return

    # succeeded, look up the flag and return it
    async with global_lock:
        curr.execute(
            "SELECT flag FROM flags WHERE contract_addr = ? AND root = ?",
            (c, str(found_tag))
        )
        flag = curr.fetchone()[0]
        writer.write(f'FLAG {flag}\n'.encode('ascii'))
        await writer.drain()
    l.info('succeeded getflag')


async def benign(reader, writer, w3):
    ip = (await reader.readline()).decode('ascii').strip()

    if ip not in ip_to_team_addr:
        l.error(f'bad ip supplied, unknown: {ip}')
        return

    # find the current target contract for this team
    team_addr = ip_to_team_addr[ip]

    registry_contract = w3.eth.contract(address=reg_contract_addr, abi=REGISTRY_CONTRACT_ARTIFACT['abi'])
    c = registry_contract.functions.getContract(team_addr).call()

    team_contract = w3.eth.contract(address=c, abi=CONTRACT_ARTIFACT['abi'])
    l.info(f'running benign against team_addr {team_addr}, contract {c}')

    # pick which benign
    choice = random.choice([benign_phony_root,]) # NOTE begin_pull_token is bugged rn
    await choice(reader, writer, w3, c, team_contract)
    l.info(f'done benign on {c}')
    writer.write(b'SUCCESS\n')
    await writer.drain()
    # next line will be <ip>

async def benign_phony_root(reader, writer, w3, c, team_contract):
    """
    Benign operation that uses one of our phony addresses
    to register a root. This root doesn't give flags, though!
    """
    # pick a phony address
    chosen_phony = random.choice(glob.glob('keys/phony/*.pub'))
    with open(chosen_phony) as fin:
        addr = fin.read().strip()
        if not addr.startswith('0x'):
            addr = '0x' + addr
        addr = w3.toChecksumAddress(addr)
    with open(chosen_phony.replace('.pub', '.key')) as fin:
        key = fin.read().strip()
    l.info(f'benign phony set root against {c} with addr {addr}')

    h = hashlib.md5()
    h.update(bytes(random.randint(0, 255) for _ in range(10)))
    h.update(b'My super secret hash salt that nobody could ever guess because it is entirely too long.\n')
    d = h.digest()
    root = w3.toInt(d)

    async with global_lock:
        trying_nonce = w3.eth.get_transaction_count(addr)
        for i in range(500):
            l.info(f'On attempt number {i+1} for nonce')
            my_nonce = trying_nonce + i
            txn = team_contract.functions.registerRoot(root).buildTransaction({'from': addr})
            txn['nonce'] = my_nonce
            txn['chainId'] = w3.eth.chain_id
            txn['gasPrice'] = w3.eth.gas_price
            signed = w3.eth.account.sign_transaction(txn, key)
            try:
                txn_hash = w3.eth.send_raw_transaction(signed.rawTransaction).hex()
                break
            except Exception as e:
                if 'replacement transaction underpriced' in str(e):
                    l.info('nonce failed, retrying')
                    continue
                writer.write(b'FAILED\n')
                await writer.drain()
                raise e
        else:
            writer.write(b'FAILED\n')
            await writer.drain()
            raise Exception('nonce failed too many times')
    l.info(f'Transmitted transaction hash {txn_hash}')

    # see if it completes
    start = time.time()
    while time.time() - start < 60: # 60s timeout, idk
        l.info(f'Watching to ensure completion of {txn_hash}')
        new_txn = w3.eth.get_transaction(txn_hash)
        if new_txn['blockNumber'] is not None:
            break
        await asyncio.sleep(1)
    else:
        l.error(f'TIMEOUT on transaction {txn_hash}')


async def benign_pull_token(reader, writer, w3: web3.Web3, c, team_contract):
    """
    Benign operation that pulls a token
    """
    l.info(f'pulling a token through {c}')
    async with global_lock:
        txn = team_contract.functions.requestToken(admin_addr).buildTransaction({'from': admin_addr})
        txn['nonce'] = w3.eth.get_transaction_count(admin_addr)
        txn['chainId'] = w3.eth.chain_id
        txn['gasPrice'] = w3.eth.gas_price
        signed = w3.eth.account.sign_transaction(txn, admin_key)
        try:
            txn_hash = w3.eth.send_raw_transaction(signed.rawTransaction).hex()
        except Exception as e:
            writer.write(b'FAILED\n')
            await writer.drain()
            raise e
    l.info(f'Transmitted transaction hash {txn_hash}')

    # see if it completes
    start = time.time()
    while time.time() - start < 60: # 60s timeout, idk
        l.info(f'Watching to ensure completion of {txn_hash}')
        new_txn = w3.eth.get_transaction(txn_hash)
        if new_txn['blockNumber'] is not None:
            #
            # TODO ensure that the receipt parses with a transaction event
            break
        await asyncio.sleep(1)
    else:
        l.error(f'TIMEOUT on transaction {txn_hash}')

    new_txn['']

async def exploit(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, _):
    flag_token = (await reader.readline()).decode('ascii').strip()

    parts = flag_token.split(';')
    if not len(parts) == 2 or not ':' in parts[0] or not ':' in parts[1]:
        l.error(f'malformed flag token: {flag_token}')
        return

    contract = parts[0].split(':')[1]
    root = parts[1].split(':')[1]

    if not root.isdigit():
        l.error(f'malformed root (expected digits): {root}')
        return

    if not web3.Web3.isChecksumAddress(contract):
        l.error(f'admin supplied a non-checksum address: {contract}')
        return

    hextag = hex(int(root))

    l.info(f'running exploit against victim contract {contract}')

    p = await asyncio.create_subprocess_exec(
        'python3',
        'exploit.py',
        '--address', contract,
        '--hextag', hextag,
        stdout=asyncio.subprocess.PIPE,
    )
    try:
        while True:
            line = await asyncio.wait_for(p.stdout.readline(), timeout=60)
            if line == b'':
                # end of output
                break
            line = line.decode('ascii').strip()
            l.info(f'exploit.py | {line}')
            writer.write(line.encode('ascii') + b'\n')
        await writer.drain()
    except asyncio.exceptions.TimeoutError:
        l.exception('Timed out waiting for exploit.py')
    finally:
        if p.returncode is not None:
            p.kill()

    return


async def handle_admin(reader, writer):
    w3 = web3.Web3(web3.WebsocketProvider('ws://127.0.0.1:8546'))
    if not w3.isConnected():
        writer.close()
        await writer.wait_close()
        return
    l.info(f'connected to web3, chainId={w3.eth.chain_id}')

    writer.write(b'hello\n')
    await writer.drain()

    # from here they can either getflag, setflag, or benign
    line = await reader.readline()
    if line == b'getflag\n':
        await getflag(reader, writer, w3)
    elif line == b'setflag\n':
        await setflag(reader, writer, w3)
    elif line == b'benign\n':
        await benign(reader, writer, w3)
    elif line == b'exploit\n':
        await exploit(reader, writer, w3)
    else:
        l.warning(f'Unknown command: {line}')
    await writer.drain()


async def attempt_claim_token(
            w3: web3.Web3,
            address: str,
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter,
            victim: str,
            tokenId: int
        ):
    root = tokenId >> 128
    l.info(
        f'Team addr={address} is attempting to claim tokenId={tokenId} from victim_addr={victim} (root={root})'
    )
    
    # see if we even recognize this as possibly having flags
    async with global_lock:
        # contract_addr TEXT, root TEXT, flag TEXT,
        curr.execute(
            """
            SELECT flag
            FROM flags
            WHERE contract_addr = ? AND root = ?
            """,
            (victim, str(root)),
        )
        maybe_flag = curr.fetchall()
        if len(maybe_flag) > 0:
            flag = maybe_flag[0][0]
            l.info('selected a flag')
        else:
            flag = None
    
    if flag is None:
        writer.write(b'No flag for that token, sorry!\n')
        await asyncio.wait_for(writer.drain(), timeout=10)
        return
    
    # see if the sender owns that flag
    team_contract: web3.contract.Contract = w3.eth.contract(
        address=victim,
        abi=CONTRACT_ARTIFACT['abi']
    )
    try:
        owner = team_contract.functions.ownerOf(tokenId).call()
        owner = w3.toChecksumAddress(owner)
    except:
        l.exception(f'Could not find owner of tokenId={tokenId} on contract {victim}')
        writer.write(b'Could not find owner of that tokenId.\n')
        await asyncio.wait_for(writer.drain(), timeout=10)
        return

    if owner != address:
        l.info(f'Team {address} attempted to claim token owned by {owner} and was denied')
        writer.write(b'No flag for that token, sorry!\n')
        await asyncio.wait_for(writer.drain(), timeout=10)
    
    # They got the flag!
    l.info(f'Team {address} used tokenId={tokenId} from victim_addr={victim} (root={root}) to claim a flag!')
    writer.write(f'FLAG: {flag}\n'.encode('ascii'))


async def handle_team(address: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # connect to web3
    w3 = web3.Web3(web3.WebsocketProvider('ws://127.0.0.1:8546'))
    if not w3.isConnected():
        writer.close()
        await asyncio.wait_for(writer.wait_close(), timeout=10)
        return
    l.info(f'connected to web3, chainId={w3.eth.chain_id}')

    # set a deadline to avoid teams using idle connections
    while True:

        #
        # What is the victim contract
        #
        writer.write(b'Claiming flags. Enter victim contract address:\n')
        await asyncio.wait_for(writer.drain(), timeout=10)
        line = await asyncio.wait_for(reader.readline(), timeout=10)
        if line == b'':
            l.debug('connection closed')
            writer.close()
            await asyncio.wait_for(writer.wait_closed(), timeout=10)
            return
        try:
            victim = line.decode('ascii').strip()
        except UnicodeDecodeError:
            writer.write(b'Could not decode response. Bye.\n')
            await asyncio.wait_for(writer.drain(), timeout=10)
            writer.close()
            await asyncio.wait_for(writer.wait_closed(), timeout=10)
            return
        try:
            victim = web3.Web3.toChecksumAddress(victim)
        except:
            l.warning(f'failed to translate {victim} to checksum address')
            writer.write(b'Invalid address. Bye.\n')
            await asyncio.wait_for(writer.drain(), timeout=10)
            writer.close()
            await asyncio.wait_for(writer.wait_closed(), timeout=10)
            return

        #
        # What is the claimed NFT ID
        #
        writer.write(b'Enter NFT tokenId (as decimal):\n')
        line = await asyncio.wait_for(reader.readline(), timeout=10)
        try:
            tokenIdSz = line.decode('ascii').strip()
        except UnicodeDecodeError:
            writer.write(b'Could not decode response. Bye.\n')
            await asyncio.wait_for(writer.drain(), timeout=10)
            writer.close()
            await asyncio.wait_for(writer.wait_closed(), timeout=10)
            return
        try:
            tokenId = web3.Web3.toInt(text=tokenIdSz)
        except:
            writer.write(b'Could not interpret tokenId as int. Bye.\n')
            await asyncio.wait_for(writer.drain(), timeout=10)
            writer.close()
            await asyncio.wait_for(writer.wait_closed(), timeout=10)
            return
        
        await attempt_claim_token(w3, address, reader, writer, victim, tokenId)


async def handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    l.info('got connection, checking credentials')
    writer.write(b'Enter your team\'s wallet address:\n')

    await asyncio.wait_for(writer.drain(), timeout=10)
    line = await asyncio.wait_for(reader.readline(), timeout=10)

    try:
        address = line.decode('ascii').strip()
    except UnicodeDecodeError:
        writer.write(b'Could not decode response. Bye.\n')
        await asyncio.wait_for(writer.drain(), timeout=10)
        writer.close()
        await asyncio.wait_for(writer.wait_closed(), timeout=10)
        return

    writer.write(f'Enter HEX(SHA1(flag_token)):\n'.encode('ascii'))
    await asyncio.wait_for(writer.drain(), timeout=10)
    line = await asyncio.wait_for(reader.readline(), timeout=10)

    try:
        password = line.decode('ascii').strip()
    except UnicodeDecodeError:
        writer.write(b'Could not decode response. Bye.\n')
        await asyncio.wait_for(writer.drain(), timeout=10)
        writer.close()
        await asyncio.wait_for(writer.wait_closed(), timeout=10)
        return

    # admin 'backdoor' / hard-coded login (sorry!)
    if address == 'admin' and password == '4e37ef8e-d04b-4269-ae1f-f7bce36dce02':
        l.info('admin login')
        await handle_admin(reader, writer)
        l.info('admin request handled')
        return

    if not address.startswith('0x'):
        address = '0x' + address
    try:
        address = web3.Web3.toChecksumAddress(address)
    except:
        l.warning(f'failed to translate {address} to checksum address')
        writer.write(b'Invalid address. Bye.\n')
        await asyncio.wait_for(writer.drain(), timeout=10)
        writer.close()
        await asyncio.wait_for(writer.wait_closed(), timeout=10)
        return

    # sleep a random amount to prevent (potential?) timing attacks
    await asyncio.sleep(random.randint(10, 100) / 1000)

    if password.startswith('0x'):
        password = password[2:]
    try:
        password = bytes.fromhex(password)
    except:
        l.warning(f'failed to decode password hex')
        writer.write(f'Could not parse {password} as hex'.encode('ascii'))
        await asyncio.wait_for(writer.drain(), timeout=10)
        writer.close()
        await asyncio.wait_for(writer.wait_closed(), timeout=10)
        return

    # see if we have anyone by this name
    if address in team_addr_to_sha1_token and password == team_addr_to_sha1_token[address]:
        l.info(f'Team login {address}')
        await handle_team(address, reader, writer)
        return

    writer.write(b'Invalid credentials.\n')
    await asyncio.wait_for(writer.drain(), timeout=10)
    writer.close()
    await asyncio.wait_for(writer.wait_closed(), timeout=10)
    return

async def main():
    async def handler_wrapper(reader, writer: asyncio.StreamWriter):
        try:
            await handler(reader, writer)
        except asyncio.exceptions.TimeoutError:
            l.info('Connection timeout')
            writer.close()
            await asyncio.wait_for(writer.wait_closed(), timeout=10)
    server = await asyncio.start_server(handler_wrapper, host='0.0.0.0', port=8443, backlog=200)
    l.info('listening on 8443')
    await server.serve_forever()

asyncio.run(main())

