#!/bin/bash

SCP_DEST=$1
TEAM_ID=$2

scp service/USERS.DAT service/USERDATA.DAT service/StockJobber service/run.sh $SCP_DEST
