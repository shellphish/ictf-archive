FROM ubuntu:20.04

ADD ro/oly /home/chall/service/ro/oly
ADD ro/consensus.olc /home/chall/service/ro/consensus.olc

WORKDIR /home/chall/service/   
CMD ["/home/chall/service/ro/oly", "/home/chall/service/ro/consensus.olc"]
