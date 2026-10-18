import web3
import json
import sys

target = sys.argv[1]
print('targeting', target)

cxn = web3.Web3(web3.IPCProvider("/opt/buffalo/data/web3_server/geth.ipc"))

print(cxn.isConnected())

with open('PhishToken.json') as fin:
    art = json.load(fin)

contract = cxn.eth.contract(address=target, abi=art['abi'])

f = contract.events.Transfer().createFilter(fromBlock=0, toBlock='latest')

l = f.get_all_entries()
for x in l:
    print(x)

