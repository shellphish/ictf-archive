# iCTF 2010 — WeirdTCP (S7)
# Original: C service implementing custom "Litya Internet Protocol"
# Extracted from iCTF2010_Service_Base.vmdk (Ubuntu Server 10.10 32-bit, 32-bit ELF)

FROM debian:buster-slim
RUN dpkg --add-architecture i386 && \
    apt-get update && apt-get install -y libc6-i386 && \
    rm -rf /var/lib/apt/lists/*
RUN useradd -u 31337 -ms /bin/bash seclab
WORKDIR /home/seclab
COPY src/weirdtcp.bin ./weirdtcp
RUN chmod +x ./weirdtcp && chown -R seclab:seclab /home/seclab
EXPOSE 3333
USER seclab
CMD ["./weirdtcp"]
