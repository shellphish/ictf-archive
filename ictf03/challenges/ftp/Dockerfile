FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libxcrypt-dev \
    && rm -rf /var/lib/apt/lists/*

# ftpd calls getpwnam("ftp") to drop privileges
RUN useradd -r -d /var/ftp -s /sbin/nologin ftp 2>/dev/null || true && \
    mkdir -p /var/ftp && \
    chown ftp:ftp /var/ftp

ARG FLAG=bcd7ab1b9a91a790e4dcd1e50ab859a0
ARG PASS=secret

WORKDIR /build
COPY src/weirdftp.c .
RUN sed "s/##FTP_FLAG##/${FLAG}/g; s/##FTP_PASS##/${PASS}/g" weirdftp.c > ftpd.c && \
    gcc -DLINUX -o /usr/local/sbin/ftpd ftpd.c -lcrypt && \
    chmod 700 /usr/local/sbin/ftpd && \
    rm -rf /build

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

WORKDIR /var/ftp
EXPOSE 21/tcp
EXPOSE 2020/tcp
ENTRYPOINT ["/docker-entrypoint.sh"]
