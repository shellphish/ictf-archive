#!/bin/sh

SCP_DEST=$1
TEAM_ID=$2

python -c "import game_server; import Board"

scp run.sh "$SCP_DEST"
scp Board.pyc "$SCP_DEST"
scp game_server.pyc "$SCP_DEST"
