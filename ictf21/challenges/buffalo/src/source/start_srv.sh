#!/bin/bash

set -e

function stop_srv() {
    echo 'Shutting down...';
    kill `cat data/miner/PID` || true;
    kill `cat data/web3_server/PID` || true;
    kill `cat data/trickler.pid` || true;
    wait;
    echo 'done'
}
trap stop_srv INT TERM HUP

echo password > /tmp/password.tmp

#
# Sanity checks
#
if [ ! -d data ];
then
    echo 'Could not find data/ directory, quitting'
    exit 1
fi;

if [ ! -f bin/geth/geth ];
then
    echo 'Could not find geth binary'
    exit 1
fi;

#
# Setups
#
if [ ! -f data/.accounts ];
then
    echo 'Loading accounts';
    if [ ! -f keys/admin.key ];
    then
        echo 'Could not find keys/admin.key';
        exit 1
    fi;
    bin/geth/geth account import --datadir data/miner --password /tmp/password.tmp keys/admin.key;
    touch data/.accounts;
fi;


#
# Genesis init
#
if [ ! -f data/.created ];
then
    echo 'Loading genesis'
    if [ ! -f genesis.json ];
    then
        echo 'Could not find genesis.json'
        exit 1
    fi
    bin/geth/geth init --datadir data/miner genesis.json
    bin/geth/geth init --datadir data/web3_server genesis.json
    touch data/.created
fi;

#
# Start up the clients
#
echo 'Starting blockchain clients'

./bin/geth/geth \
    --password /tmp/password.tmp \
    --datadir "data/miner" \
    --networkid 40245 \
    --syncmode full \
    --miner.gaslimit 80000000 \
    --txpool.locals '0x1C7F0000495312005Be35245d025850bd41760b1' \
    --txpool.accountslots 400 \
    --txpool.globalslots 10000 \
    --txpool.accountqueue 400 \
    --txpool.globalqueue 4096 \
    --port 4100 \
    --netrestrict '127.0.0.1/32' \
    --unlock "0x`cat keys/admin.pub`" \
    --verbosity 3 \
    --nodiscover \
    --mine 2>> data/miner/log.txt > /dev/null &
echo "$!" > data/miner/PID

cat << EOF > data/miner/start.sh
#!/bin/bash
pushd `pwd`
./bin/geth/geth \\
    --password /tmp/password.tmp \\
    --datadir "data/miner" \\
    --networkid 40245 \\
    --syncmode full \\
    --miner.gaslimit 100000000 \\
    --txpool.locals '0x1C7F0000495312005Be35245d025850bd41760b1' \\
    --txpool.accountslots 400 \\
    --txpool.globalslots 10000 \\
    --txpool.accountqueue 400 \\
    --txpool.globalqueue 4096 \\
    --port 4100 \\
    --netrestrict '127.0.0.1/32' \\
    --unlock "0x\`cat keys/admin.pub\`" \\
    --verbosity 3 \\
    --nodiscover \\
    --mine 2>> data/miner/log.txt > /dev/null &
echo "\$!" > data/miner/PID
popd
EOF
chmod +x data/miner/start.sh

# set miner's iptables
echo 'setting iptables to firewall miner...';
# allow localhost connections
iptables -A INPUT -p tcp -s localhost --dport 4100 -j ACCEPT
iptables -A INPUT -p tcp --dport 4100 -j REJECT --reject-with tcp-reset
iptables -A INPUT -p udp --dport 4100 -j REJECT

echo 'Started. Waiting a bit to get ENODE'
sleep 5
echo 'Getting enode...'

# get the enode
ENODE1=`./bin/geth/geth attach --exec 'admin.nodeInfo.enode' --datadir data/miner | cut -d'"' -f2`
echo "ENODE1 = $ENODE1"

echo "$ENODE1" > data/miner/enode

echo 'Sleeping a bit to wait for some blocks to be mined'
sleep 30

# start the web3 client
echo '[*] start web3 client';
./bin/geth/geth \
    --verbosity 5 \
    --datadir data/web3_server \
    --networkid 40245 \
    --syncmode full \
    --port 4102 \
    --maxpeers 1024 \
    --txpool.locals '0x1C7F0000495312005Be35245d025850bd41760b1' \
    --txpool.accountslots 400 \
    --txpool.globalslots 10000 \
    --txpool.accountqueue 400 \
    --txpool.globalqueue 4096 \
    --ws \
    --ws.addr 127.0.0.1 \
    --ws.origins '*' \
    --bootnodes '' \
    --nodekey keys/bootnode.key \
    2>> data/web3_server/log.txt > /dev/null &
echo "$!" > data/web3_server/PID

cat << EOF > data/web3_server/start.sh
#!/bin/bash
pushd `pwd`
./bin/geth/geth \\
    --verbosity 5 \\
    --datadir data/web3_server \\
    --networkid 40245 \\
    --syncmode full \\
    --port 4102 \\
    --maxpeers 1024 \\
    --txpool.locals '0x1C7F0000495312005Be35245d025850bd41760b1' \\
    --txpool.accountslots 400 \\
    --txpool.globalslots 10000 \\
    --txpool.accountqueue 400 \\
    --txpool.globalqueue 4096 \\
    --ws \\
    --ws.addr 127.0.0.1 \\
    --ws.origins '*' \\
    --bootnodes '' \\
    --nodekey keys/bootnode.key \\
    2>> data/web3_server/log.txt > /dev/null &
echo "\$!" > data/web3_server/PID
popd
EOF
chmod +x data/miner/start.sh

sleep 5
# get the enode
ENODE2=`./bin/geth/geth attach --exec 'admin.nodeInfo.enode' --datadir data/web3_server | cut -d'"' -f2`
echo "ENODE2 = $ENODE2"
echo "$ENODE2" > data/web3_server/enode

# manually add peer
./bin/geth/geth attach --exec "admin.addPeer(\"$ENODE1\")" --datadir data/web3_server

# start trickling
python3 trickle_ether.py > data/trickle_log.txt &
echo "$!" > data/trickler.pid

sleep 10

# deploy initial contracts
python3 deploy_team_default_contract.py | tee -a data/default_contract_deploy_log.txt

# launch the flag server
ulimit -n 4096
python3 flag_srv.py | tee -a data/flag_srv_log.txt;

echo '[!!!!!!!!!] flag_srv died SHOULD NOT HAPPEN'

sleep infinity
