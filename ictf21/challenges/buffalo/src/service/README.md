# Buffalo, ltd. is launching a revolutionary token service

Your team was hired to oversee the rollout of Buffalo, ltd.'s
revolutionary new token-based trading card system. In
this system, each trading card is an NFT on our new private blockchain.

Each NFT has a 256-bit ID. The high 128 bits are a 'root' tag indicating
the type of trading card, and the low 128 bits are a serial number.

Users reserve their 128 bit root by calling the function `registerRoot(uint128 root)`
on your team's smart contract. Then, that user has the exclusive right to mint
NFTs derived from that `root` using the function `requestToken(uint128 root, address to)`.

The game admin is operating at address `0x1C7F0000495312005Be35245d025850bd41760b1`.
We will periodically invoke `registerRoot(...)` on your smart contract, and
call `requestToken(..)` to mint tokens for our root id.

## Your team's wallet

Your team is assigned a wallet on the blockchain. Run `cd ro && node derive_keys.js <YOUR_FLAG_TOKEN>` to get
your public / private key pair. We have already used your wallet to deploy the default smart contract.
You will regularly receive ether to operate on our private blockchain.

## Connecting to the blockchain

`ro/start.sh` starts up `geth` and connects to our private blockchain.

## Getting flags

The flag ID is of the form `CONTRACT:<address>;ROOT:<number>`.
The admin has reserved the given root for themselves.
You must attack the victim smart contract at `address` by forcing it
to send you a token with that root.
Contact the flag server at `18.144.138.34:8443` and follow the instructions to verify
the stolen NFT and receive your flag.

## Patching

The smart contract at address `0x888888881796763aF2815d8b225052DAacC3DBbF` holds our registry for 
smart contracts. After deploying a new smart contract, use your team's wallet to call `register(address a)` where `a` is the new smart contract's address. 


## Meta-info

Your contract's ABI is at `ro/token_abi.json`.

Our registry's ABI is at `ro/registry_abi.json`.

The contract `0xBADBAD6ef6306E5ba9492fA50a54e8143B7f6643` contains the default contract, for reference.

