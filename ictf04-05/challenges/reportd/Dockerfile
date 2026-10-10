# iCTF 2005 — reportd (Report filing daemon)
# C daemon that stores report data to a file with locking.
#
# Build:  docker build -t ictf0405-reportd .
# Run:    docker run -p 7003:7003 ictf0405-reportd

FROM debian:bookworm-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends gcc make && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY src/ /build/
RUN make

FROM debian:bookworm-slim
WORKDIR /opt/reportd
COPY --from=builder /build/reportd ./
RUN useradd -u 31337 -ms /bin/bash challenge && \
    chown challenge /opt/reportd
EXPOSE 7003
USER challenge
CMD ["/opt/reportd/reportd"]
