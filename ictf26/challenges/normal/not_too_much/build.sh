#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Give the source name"
    echo "Example: bof_32.c"
    exit 1
fi

out=$(echo "$1" | cut -d . -f 1)
gcc -O0 -fno-stack-protector -fno-stack-check -z execstack -m64 -no-pie -fno-optimize-sibling-calls -g "$1" -o "$out"
