#!/usr/bin/env python3
"""
gen_phonies.py
generate phony addresses to mask player-teams

Phonies are stored under keys/phony/
"""

import os
import shutil
import web3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('NUM_ADDRS', type=int)

args = parser.parse_args()

if os.path.isdir('keys/phony'):
    answer = input('Delete and re-generate keys/phony? [y/N] ')
    if answer.lower() != 'y':
        print('quitting.')
        exit(1)
    shutil.rmtree('keys/phony')

os.mkdir('keys/phony')

w3 = web3.Web3()
for i in range(args.NUM_ADDRS):
    addr = w3.eth.account.create()
    with open(f'keys/phony/{i}.pub', mode='w') as fout:
        fout.write(addr.address[2:] + '\n')
    with open(f'keys/phony/{i}.key', mode='w') as fout:
        fout.write(addr.key.hex()[2:] + '\n')

print(f'Generated {args.NUM_ADDRS} in keys/phony/')
