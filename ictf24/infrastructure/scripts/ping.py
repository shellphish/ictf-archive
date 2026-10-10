"""
Ping challenges to check for liveness.

USAGE: python3 scripts/ping.py [CHALLENGES...]

If no challenges are specified, all challenges are pinged.
"""

import sys
import requests
import socket
import traceback
import yaml
import typing
import argparse
import os
from pathlib import Path
import json
import configparser

TIMEOUT = 2

def main():
    global TIMEOUT
    parser = argparse.ArgumentParser(description='Ping challenges to check for liveness.')
    parser.add_argument('CHALLENGES', nargs='*', help='Challenges to ping (default: all)')
    parser.add_argument('--timeout', type=int, help='set the timeout (seconds)')
    args = parser.parse_args()

    challenges = gather_challenges()

    if args.timeout:
        TIMEOUT = args.timeout

    if args.CHALLENGES:
        names_to_challenges = {challenge.name: challenge for challenge in challenges}
        assert len(names_to_challenges) == len(challenges), "Duplicate challenge names"

        new_challenges = []
        for name in args.CHALLENGES:
            if name not in names_to_challenges:
                print(f"Error: challenge not found: {name}")
                return
            challenge = names_to_challenges[name]
            new_challenges.append(challenge)

    print(f'Pinging {len(challenges)} challenges...')
    challenges.sort(key=lambda c: c.name)

    had_failures = False

    for challenge in challenges:
        print(f"Pinging {challenge.name}...", end=' ')
        sys.stdout.flush()
        if ping_challenge(challenge):
            # Print in green terminal color
            print("\033[92mPASS\033[0m")
        else:
            # Print in red terminal color
            print("\033[91mFAIL\033[0m")
            had_failures = True
    
    if had_failures:
        exit(1)
    else:
        exit(0)
        

def gather_challenges() -> typing.List['Challenge']:
    challenges = []
    challenges.extend(gather_challenges_in_dir(Path('high-challenges')))
    challenges.extend(gather_challenges_in_dir(Path('under-challenges')))
    
    return challenges

def gather_challenges_in_dir(directory: Path) -> typing.List['Challenge']:
    # Find challenges in the .ctf directory
    config_file = directory / '.ctf' / 'config'
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    config = configparser.ConfigParser()
    config.read(config_file)

    challenges = []
    for dirname in sorted(config['challenges'].values()):
        # remove trailing slash if it exists
        dirname = dirname.rstrip('/')

        maybe_chall = extract_challenge_details(directory / dirname)
        if maybe_chall is not None:
            challenges.append(maybe_chall)
    
    return challenges

def extract_challenge_details(directory: Path) -> typing.Optional['Challenge']:
    challenge_yml = directory / 'challenge.yml'

    if not challenge_yml.exists():
        raise FileNotFoundError(f"challenge.yml not found: {challenge_yml}")

    with open(challenge_yml) as f:
        data = yaml.safe_load(f)
    
    kind = data.get('protocol')
    if kind is None:
        # not a pingable challenge
        return None

    assert kind in ['tcp', 'http'], f"Invalid protocol: {kind}"

    # Look for a connection_info
    cxn_info = data.get('connection_info')
    if cxn_info is None:
        # Not deployed
        return None
    
    name = data['name']

    if kind == 'tcp':
        assert cxn_info.startswith('nc ')
        host, port = cxn_info[3:].strip().split(' ')
        port = int(port)

        return Challenge(name, host, port, 'tcp')
    else:
        assert kind == 'http'
        assert cxn_info.startswith('https://')
        domain = cxn_info[8:]
        port = 443

        return Challenge(name, domain, port, 'http')

def ping_challenge(challenge: 'Challenge') -> bool:
    if challenge.kind == 'tcp':
        return ping_tcp(challenge)
    else:
        return ping_http(challenge)

def ping_tcp(challenge: 'Challenge') -> bool:
    try:
        with socket.create_connection((challenge.domain, challenge.port), timeout=TIMEOUT) as s:
            # Attempt to read one byte (should greet us with a banner)
            s.recv(1)
        return True
    except Exception as e:
        traceback.print_exc()
        return False

def ping_http(challenge: 'Challenge') -> bool:
    try:
        resp = requests.get(f'https://{challenge.domain}/', timeout=TIMEOUT)
        if resp.status_code != 200:
            print(f"HTTP error: {resp.status_code}")
        return resp.status_code == 200
    except Exception as e:
        traceback.print_exc()
        return False

class Challenge(typing.NamedTuple):
    name: str
    domain: str
    port: int
    kind: typing.Literal['tcp', 'http']

if __name__ == '__main__':
    main()
