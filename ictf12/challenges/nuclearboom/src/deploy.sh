#!/bin/bash

SCP_DEST=$1
TEAM_ID=$2

scp run.sh $SCP_DEST
scp nuclearboom $SCP_DEST
scp .selfdestruction $SCP_DEST

# generate team-specific password
TMPPASS=`tempfile`
echo -n "$TEAM_ID-mylittlesecret-$TEAM_ID" | sha256sum | cut -d" " -f1 > $TMPPASS
scp $TMPPASS $SCP_DEST/.password
rm $TMPPASS
