FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive    
# golang version: 1.17.3
#RUN wget https://golang.org/dl/go1.17.3.linux-amd64.tar.gz && \
#    rm -rf /usr/local/go && tar -C /usr/local -xzf go1.17.3.linux-amd64.tar.gz \
#    export PATH=$PATH:/usr/local/go/bin 

RUN useradd -m --uid 31337 chall
WORKDIR /home/chall/service/   

CMD ["/home/chall/service/ro/gopher_coin"]