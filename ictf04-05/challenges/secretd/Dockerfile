# iCTF 2005 — secretd (Secret storage daemon)
# C service with public/private interfaces.
#
# Build:  docker build -t ictf0405-secretd .
# Run:    docker run -p 7004:7004 ictf0405-secretd

FROM debian:bookworm-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc make autoconf automake && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY src/ /build/
RUN autoreconf -fi 2>/dev/null || true && ./configure && make

FROM debian:bookworm-slim
WORKDIR /opt/secretd
COPY --from=builder /build/secretd* ./
RUN useradd -u 31337 -ms /bin/bash challenge
EXPOSE 7004
USER challenge
CMD ["/opt/secretd/secretd"]
