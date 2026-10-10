#!/bin/bash

docker build -t ictf/try_more:latest -f Dockerfile .
docker compose up -d

# now run exploit on 4445
