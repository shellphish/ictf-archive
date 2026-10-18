#!/usr/bin/env python3

import json
import os

if not os.path.exists('./teams_info.json'):
    print('expected ./teams_info.json to exits')
    exit(1)

with open('./teams_info.json') as fin:
    infos = json.load(fin)

with open('access_tokens.txt', mode='w') as fout:
    for team in infos['teams']:
        host = 'team' + str(team['id'])
        flag_token = team['flag_token']
        assert len(flag_token) > 0
        fout.write(f'{host} {flag_token}\n')

