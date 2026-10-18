# Challenge codename "Buffalo"

This is a challenge for iCTF 2021.

Unlike other challenges, this one occurs on a blockchain. Each team owns a smart contract. Attackers steal NFTs from victim smart contracts. Defenders patch by deploying and registering a new, patched smart contract.

## Special nuance

This breaks with the service-oriented tradition of iCTF.
Team VMs come pre-loaded with a blockchain client, but their "service" itself runs in the shared distributed ledger.

Considering that there can be no "private" data on the blockchain, we cannot store flags directly on-chain. 
Instead, we run a central flag registry which verifies fraudulently minted NFTs, and distributes flags to their holders.

## Setup instructions

First, you must prepare a number of secrets.

We need two pieces of information for each team: (1) their access token and (2) their network DNS name.
Their access token is a private piece of information used to derive the team's wallet address.
The DNS name is necessary because `setflag` is given that information but must map it to the wallet address.

So, ensure that `source/access_tokens.txt` contains that information. The file should be as follows:

```
<hostname> <access token>
<hostname> <access token>
<hostname> <access token>
...
```

Then, call this helper to generate their the file `source/allkeys.txt` which contains their keypairs:

```
cd source
npm install
./gen_pubkeys.sh
```

 __TODO document this process__

### The game container

This container runs four important services, plus some one-time setup scripts.

1. __The block miner.__ This service is the block authority for our private PoA blockchain. The miner does not "mine" in the traditional sense, but signs blocks at a regular interval. Clients are configured to only accept blocks with our signature. This service is intentionally _not_ exposed to outside traffic, to minimize intrusion risk. iptables within the container is configured to drop (via tcp RST) non-local traffic.

2. __The blockchain server.__ This service exposes two important servers: (1) the ethereum blockchain wire protocol which team VMs use to bootstrap our blockchain, and (2) a locally exposed web3 websocket server which we use locally to manipulate the blockchain.

3. __The ether trickler.__ This service distributes ether at a fixed rate from our very rich admin account. Distributions occur at a fixed interval.

4. __The flag server.__ This service does flag operations. When the game calls `setflag`, this service manipulates the blockchain to register the new flag token on the (potential) victim contract. It also distributes flags to teams that connect and present evidence of a stolen NFT.

__Building__

```
cd source
# npm install # You don't need to run this a second time but make sure it was run once
# npx hardhat compile # not needed right now, precompiled artifacts already included
docker build -t chall_buffalo_srv .
docker run \
    --cap-add=NET_ADMIN \
    --rm \
    -p 8443:8443 \
    -p 4102:4102 \
    -v `realpath data`:/opt/buffalo/data \
    --name chall_buffalo_srv \
    chall_buffalo_srv
```
