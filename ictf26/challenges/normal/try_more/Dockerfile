FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libc6-dev \
        xinetd \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash ctf

WORKDIR /challenge

COPY try_more.c .

# gcc on Ubuntu 24.04 defaults to PIE — intentional for the challenge
RUN gcc -O0 -fno-stack-protector try_more.c -o try_more && \
    chmod +x try_more && \
    rm -f try_more.c

# Entrypoint writes FLAG env var to /challenge/flag.txt at startup
COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

# Wrapper with timeout
RUN printf '#!/bin/sh\ncd /challenge\nexec timeout 120 /challenge/try_more\n' > /challenge/run.sh && \
    chmod +x /challenge/run.sh

# xinetd service configuration
RUN printf 'service ctf\n\
{\n\
    type        = UNLISTED\n\
    protocol    = tcp\n\
    socket_type = stream\n\
    port        = 4445\n\
    wait        = no\n\
    user        = ctf\n\
    server      = /challenge/run.sh\n\
    disable     = no\n\
    per_source  = 50\n\
    rlimit_cpu  = 120\n\
}\n' > /etc/xinetd.d/ctf

ENV FLAG=ictf{aslR-1s-n0t-always-th@t-b@d}

EXPOSE 4445

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/sbin/xinetd", "-dontfork"]