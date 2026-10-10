# iCTF 2005 — ccauthd (Silly Auth Server)
# Simple C auth daemon. REG/AUTH/REVOKE/STATUS/PING/QUIT protocol.
#
# Build:  docker build -t ictf0405-ccauthd .
# Run:    docker run -p 7002:7002 ictf0405-ccauthd

FROM debian:bookworm-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends gcc make && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY src/ /build/
RUN make

FROM debian:bookworm-slim
WORKDIR /opt/ccauthd
COPY --from=builder /build/ccauthd ./
RUN useradd -u 31337 -ms /bin/bash challenge
EXPOSE 7002
USER challenge
CMD ["/opt/ccauthd/ccauthd"]
