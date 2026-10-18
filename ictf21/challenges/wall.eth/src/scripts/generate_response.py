#!/usr/bin/env python3

import nacl.signing

SIGNING_KEY = "9df7dde503ae009bdb45d7f86054aae032aa316a858cf2529ad5bcd8d59f2a68"

def generate_response(challenge):
	key = nacl.signing.SigningKey(SIGNING_KEY, encoder=nacl.encoding.HexEncoder)
	return key.sign(challenge.encode(), encoder=nacl.encoding.HexEncoder)
