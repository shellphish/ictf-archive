FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libxcrypt-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -r -d /var/sfind -s /sbin/nologin sfind && \
    mkdir -p /var/sfind && \
    chown sfind:sfind /var/sfind

ARG FLAG=17409258fb54788411496ede00051e1a
ARG PASS=XXGvWEuD1BDMI

WORKDIR /build
COPY src/weirdfind.c .
RUN sed "s/##FIND_FLAG##/${FLAG}/g; s/##FIND_PASS##/${PASS}/g" weirdfind.c > sfind.c && \
    gcc -DLINUX -o /var/sfind/sfind sfind.c -lcrypt && \
    chown sfind:sfind /var/sfind/sfind && \
    chmod 755 /var/sfind/sfind && \
    rm -rf /build

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

WORKDIR /var/sfind
EXPOSE 31337/udp
ENTRYPOINT ["/docker-entrypoint.sh"]
