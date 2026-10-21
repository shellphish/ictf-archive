#!/bin/bash

if ! /home/challenge/src/pow.py ask 10222; then
  echo 'Proof-of-work failed'
  exit 1
fi

cd /home/challenge/src && /root/.rye/shims/rye run espresso