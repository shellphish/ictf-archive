#!/usr/bin/env python3

import nacl.signing
import sys

VERIFY_KEY = "f68f37523ad0e4d5cab780beb258efe52cf732a2c30394d09200155d2517e4ec"

if __name__ == "__main__":
	challenge = sys.argv[1]
	response = sys.argv[2]
	key = nacl.signing.VerifyKey(VERIFY_KEY, encoder=nacl.encoding.HexEncoder)
	sys.exit(key.verify(response, encoder=nacl.encoding.HexEncoder).decode() != challenge)
