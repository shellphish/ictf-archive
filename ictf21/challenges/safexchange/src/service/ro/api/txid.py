import random
import string
import time

def txidGenerator(amount):
    # this is my own tx-id generator and its off-chain
    txid = ""
    for i in range(64):
        for j in range((amount % 50) + 1):
            char = random.choice(string.ascii_letters)
            time.sleep(0.0001)
        txid += char
    return txid[-10:]
