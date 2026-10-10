# iCTF 2005 — bassretard (Bass Re-Tard remote admin service)
# C application built with autoconf/make. Network daemon.
#
# Build:  docker build -t ictf0405-bassretard .
# Run:    docker run -p 7000:7000 ictf0405-bassretard

FROM debian:bookworm-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc make autoconf automake \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY src/ /build/
RUN autoreconf -fi 2>/dev/null || true && \
    ./configure && make

FROM debian:bookworm-slim
WORKDIR /opt/bassretard
COPY --from=builder /build/bassretard* ./
RUN useradd -u 31337 -ms /bin/bash challenge
EXPOSE 7000
CMD ["/opt/bassretard/bassretard"]
