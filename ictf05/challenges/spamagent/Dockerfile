# iCTF 2005 — spamagent (Spam Agent service)
# C network daemon built with autoconf.
#
# Build:  docker build -t ictf05-spamagent .
# Run:    docker run -p 7100:7100 ictf05-spamagent

FROM debian:bookworm-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc make autoconf automake && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY src/ /build/
RUN autoreconf -fi 2>/dev/null || true && ./configure && make

FROM debian:bookworm-slim
WORKDIR /opt/spamagent
COPY --from=builder /build/spamagent* ./
RUN useradd -u 31337 -ms /bin/bash challenge
EXPOSE 7100
USER challenge
CMD ["/opt/spamagent/spamagent"]
