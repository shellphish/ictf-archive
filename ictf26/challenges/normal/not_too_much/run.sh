#!/bin/bash

docker build -t ictf/not_too_much:latest -f Dockerfile .
docker compose up -d

# now run the exploit 4444
