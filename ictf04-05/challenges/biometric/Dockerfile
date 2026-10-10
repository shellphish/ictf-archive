# iCTF 2005 — biometric (file query/store service)
# C HTTP-like service with file storage. Built with autoconf.
#
# Build:  docker build -t ictf0405-biometric .
# Run:    docker run -p 7001:7001 ictf0405-biometric

FROM debian:bookworm-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc make autoconf automake && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY src/ /build/
RUN autoreconf -fi 2>/dev/null || true && ./configure && make

FROM debian:bookworm-slim
WORKDIR /opt/biometric
COPY --from=builder /build/biometric* ./
RUN useradd -u 31337 -ms /bin/bash challenge && \
    mkdir -p /opt/biometric/store && chown challenge /opt/biometric/store
EXPOSE 7001
USER challenge
CMD ["/opt/biometric/biometric"]
