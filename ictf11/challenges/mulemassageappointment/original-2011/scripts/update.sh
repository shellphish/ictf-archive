#!/bin/bash

FLAG=$(python encrypt.py $1)
wget --header="Flag: $FLAG" --server-response http://$2:$3/putflag -O /dev/null
