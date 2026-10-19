#!/bin/bash

SCP_DEST=$1
TEAM_ID=$2
# compiles the python
python -m compileall .
# Initializes the database
./traintrain.py -i traintrain.ini

chmod 755 traintrain.pyc generate_assignment.pyc evaluate_assignment.pyc
scp traintrain.pyc "$SCP_DEST/traintrain"
scp generate_assignment.pyc "$SCP_DEST/generate_assignment"
scp evaluate_assignment.pyc "$SCP_DEST/evaluate_assignment"
scp traintrain.ico "$SCP_DEST"
scp traintrain.jpg "$SCP_DEST"
scp traintrain.db "$SCP_DEST"
scp traintrain.ini "$SCP_DEST"

scp run.sh "$SCP_DEST"
