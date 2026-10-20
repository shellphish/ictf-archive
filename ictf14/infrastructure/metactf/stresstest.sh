#!/bin/bash

INFO_FP=$1
IP=$2
NUM=$3
NO_EXPLOIT_SWITCH=$4

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TESTER_FP=$DIR/tester.py

for f in `seq $NUM`; do ($TESTER_FP --once --info $INFO_FP --ip $IP $NO_EXPLOIT_SWITCH &) ; done | grep SUCCESS | wc -l
