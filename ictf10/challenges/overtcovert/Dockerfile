# iCTF 2010 — OvertCovert (S9)
# Original: 32-bit ELF steganography service, port 1969
# Binary extracted from iCTF2010_Service_Base.vmdk; source released publicly during competition
# Start: overtcovert -s <secret_flag>

FROM debian:buster-slim
RUN dpkg --add-architecture i386 && \
    apt-get update && apt-get install -y libc6-i386 && \
    rm -rf /var/lib/apt/lists/*
RUN useradd -u 31337 -ms /bin/bash seclab
WORKDIR /home/seclab
COPY src/overtcovert.bin ./overtcovert
COPY src/decrypt.bin ./decrypt
RUN chmod +x ./overtcovert ./decrypt && chown -R seclab:seclab /home/seclab
EXPOSE 1969
USER seclab
CMD ["./overtcovert", "-s", "ictf2010{overtcovert_flag}"]
