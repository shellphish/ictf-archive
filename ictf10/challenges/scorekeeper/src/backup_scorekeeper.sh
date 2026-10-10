#!/bin/bash
DATESTR=`date '+%Y-%m-%d-%H:%M:%S'`
mysqldump -uroot -pyougottabekiddingright ictf2010 > backup.${DATESTR}

