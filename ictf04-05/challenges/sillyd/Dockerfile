# iCTF 2005 — sillyd (Silly Auth Server)
# C auth daemon listening on port 12345/tcp.
# REG/AUTH/REVOKE/STATUS/PING/QUIT protocol (same family as ccauthd).
#
# Build:  docker build -t ictf0405-sillyd .
# Run:    docker run -p 12345:12345 ictf0405-sillyd

FROM debian:bookworm-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends gcc make && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY src/sillyd.c src/Makefile* ./
# If no Makefile, build directly
RUN gcc -o sillyd sillyd.c 2>/dev/null || (make && echo "make ok")

FROM debian:bookworm-slim
WORKDIR /opt/sillyd
COPY --from=builder /build/sillyd ./
RUN useradd -u 31337 -ms /bin/bash challenge && \
    mkdir data && chown challenge data
EXPOSE 12345
USER challenge
CMD ["/opt/sillyd/sillyd"]
