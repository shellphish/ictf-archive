FROM ubuntu:22.04
RUN apt-get update && apt-get install -y build-essential
RUN apt-get install -y socat

RUN useradd -d /home/ctf/ -m -p ctf -s /bin/bash ctf
RUN echo "ctf:ctf" | chpasswd

WORKDIR /home/ctf

COPY chal .
COPY src/flag.txt .

RUN chmod +x ./chal
USER ctf
EXPOSE 3435
CMD socat TCP-LISTEN:3435,reuseaddr,fork EXEC:"./chal"
