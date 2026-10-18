FROM ubuntu:20.04

RUN apt-get update \
 && apt-get install -y python3 python3-pip socat \
 && pip3 install pynacl \
 && useradd -ms /bin/bash --uid 31337 chall

USER chall
WORKDIR /home/chall

CMD ulimit -t 300 -m 1000000 -v 1000000
CMD cd service/ro && socat TCP-LISTEN:6666,REUSEADDR,FORK EXEC:"./wall.eth"
