#!/bin/bash

set -e

echo '[*] Generating pubkeys for all teams'

if [ ! -f 'access_tokens.txt' ]; then
    echo '[!!!] access_tokens.txt must exist and contain all access tokens, one per line [!!!]';
    exit 1;
fi;


echo -n 'DESTROYING old key record; continue? [y/N] '
read line;
if [ "$line" != 'y' ]; then
    echo 'quitting, bye.';
    exit 1;
fi;


I="1"
N=`cat access_tokens.txt | wc -l`

function gen_keyrow () {
    ACCESS_TOKEN=`echo "$1" | cut -d' ' -f2 | tr -d '\n'`
    ADDR=`echo "$1" | cut -d' ' -f1 | tr -d '\n'`
    keys=`node memwallet/main.js "$ACCESS_TOKEN" | tr -d '\n'`;
    echo "$ADDR $ACCESS_TOKEN $keys"
}
export -f gen_keyrow
export SHELL=/bin/bash

echo '# ip access_token address private_key' > allkeys.txt
cat access_tokens.txt | parallel -j100% gen_keyrow >> allkeys.txt
gen_keyrow 'backdoor_dont_look_at_me a_v3ry_p00r_password_th4t_1s_l0ng_4nd_h4rd_to_guess' >> allkeys.txt
