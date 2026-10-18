FROM alpine:latest

RUN  apk add coreutils \
 &&  addgroup -S --gid 31337 chall \
 &&  adduser  -S --uid 31337 -G chall chall
COPY service /home/chall/service
RUN  mkdir -p /home/chall/service/append \
 &&  chown -R root:root /home/chall/service \
 &&  chown chall:chall /home/chall/service/append

USER chall
WORKDIR /home/chall/service
CMD ["./keys.ch", "server", "--port", "6666"]
