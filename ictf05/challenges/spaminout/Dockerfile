# iCTF 2005 — spaminout (Spam In/Out gateway)
# C network daemon: spam ingestion and delivery gateway.
#
# Build:  docker build -t ictf05-spaminout .
# Run:    docker run -p 7101:7101 ictf05-spaminout

FROM debian:bookworm-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc make autoconf automake && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY src/ /build/
RUN autoreconf -fi 2>/dev/null || true && ./configure && make

FROM debian:bookworm-slim
WORKDIR /opt/spaminout
COPY --from=builder /build/spaminout* ./
RUN useradd -u 31337 -ms /bin/bash challenge
EXPOSE 7101
USER challenge
CMD ["/opt/spaminout/spaminout"]
