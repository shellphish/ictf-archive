import web3
import json
import sys

target = sys.argv[1]
print('targeting', target)

cxn = web3.Web3(web3.IPCProvider("/opt/buffalo/data/miner/geth.ipc"))

print(cxn.isConnected())

with open('PhishToken.json') as fin:
    art = json.load(fin)

f = cxn.eth.filter({"from": target})

l = f.get_all_entries()
for x in l:
    txn = cxn.eth.get_transaction(x['transactionHash'])
    print(txn)

