FROM ubuntu:20.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y wget iputils-ping nodejs npm
WORKDIR /home/chall/service

RUN mkdir -p rw/data

COPY ro ro
RUN cd ro && npm --only=dev install
RUN chmod +x ro/start.sh

CMD ./ro/start.sh

