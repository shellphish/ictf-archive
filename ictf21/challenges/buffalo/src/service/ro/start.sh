#!/bin/bash

echo '[*] starting geth chain...'

# Initialize our genesis block
if [ ! -f rw/data/.genesis ]; then
    echo '[*] generate genesis'
    ./ro/geth/geth init --datadir ./rw/data/chaindata ro/genesis.json
    touch rw/data/.genesis
fi;

# Wait for bootnode to start
until ping -c 1 18.144.138.34; do
    echo '[*] bootnode not started yet, waiting...';
    TOSLEEP=$(( $RANDOM % 6 + 5));
    echo "Waiting for $TOSLEEP seconds"
    sleep $TOSLEEP;
done

sleep 5;

# Loop forever running geth
while true; do
    echo '[*] starting node'
    ./ro/geth/geth \
        --datadir ./rw/data/chaindata \
        --bootnodes "`cat ro/enode.boot`" \
        --port 6666 \
        --networkid 40245;
    echo '[!] node exit, sleep & try again (ctrl+c once more to quit sleep)'
    sleep 60;
done;

