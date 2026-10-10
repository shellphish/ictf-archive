#!/bin/bash
# Wrapper to bridge TCP stdin → argv for the challenge binary.
# socat connects one TCP client to one instance of this script.

echo "=== not_too_much ==="
echo "Usage: send your payload as a single line of text."
echo "Example: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
echo ""

# Read one line from the client (the payload)
read -r user_input

# Pass it as argv[1] to the vulnerable binary
exec /challenge/bof_64 "$user_input"
